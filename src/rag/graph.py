import hashlib
import logging
from typing import Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# 벡터스토어는 bootstrap.py에서 주입
db_korean: Any = None
llm: Optional[ChatOpenAI] = None


def configure_vectorstore(korean_store: Any) -> None:
    """외부에서 벡터스토어를 주입하는 초기화 함수"""
    global db_korean
    db_korean = korean_store


def configure_llm(model: str = "gpt-4.1-mini") -> None:
    global llm
    llm = ChatOpenAI(model=model)


def get_llm() -> ChatOpenAI:
    """지연 초기화로 import-time API key 오류를 방지"""
    global llm
    if llm is None:
        llm = ChatOpenAI(model="gpt-4.1-mini")
    return llm


class RAGState(TypedDict):
    user_query: str
    search_results: List[str]
    final_answer: str
    retrieval_k: Optional[int]       # vector search top-k override (default: 3)
    # P0: HyDE variant 정합 필드 (KB #01, REV_DECISION_STEP1)
    hyde_variant: Optional[str]      # "paper" | "subquery" (default: "paper")
    hypo_used: bool                  # paper variant 실행 시 True
    hypo_text_hash: Optional[str]    # hypo_doc MD5[:8], provenance 추적용


def _search_or_empty(store: Any, query: str, k: int = 3) -> List[str]:
    """스토어 미설정/오류 상황에서도 런타임이 죽지 않도록 안전 검색"""
    if store is None:
        logger.warning("Vector store is not configured. query=%s", query)
        return []
    try:
        results = store.similarity_search(query, k=k)
        return [getattr(doc, "page_content", str(doc)) for doc in results]
    except Exception:
        logger.exception("Vector search failed. query=%s", query)
        return []


# === Phase 3: HyDE 검색 노드 ===
# KB #01 HyDE (arxiv 2212.10496) — 쿼리 확장 검색 × 비정제 주입
# taxonomy: [[쿼리 확장 검색]] · Axis A
_HYDE_PROMPT = ChatPromptTemplate.from_template(
    "다음 질문에 대한 답변을 포함할 것 같은 짧은 문단을 한국어로 작성하세요.\n질문: {query}"
)
_HYDE_VARIANTS = {"paper", "subquery"}


def _generate_hypo_doc(query: str) -> str:
    """HyDE paper variant — 가상 문서 생성 (테스트 모킹 진입점)"""
    return (_HYDE_PROMPT | get_llm() | StrOutputParser()).invoke({"query": query})


def hyde_search(state: RAGState) -> RAGState:
    """KB #01 HyDE — 가상 문서 임베딩으로 벡터 검색 (Phase 3 진입점)

    variant=paper  (default): q → LLM(hypo_doc) → embed(hypo_doc) → top-k
    variant=subquery         : q → embed(q) → top-k  (hypo_doc 생성 없음)

    provenance 필드: hypo_used, hypo_text_hash (REV_DECISION_STEP1 KPI)
    """
    variant = state.get("hyde_variant") or "paper"
    if variant not in _HYDE_VARIANTS:
        raise ValueError(
            f"Unsupported hyde_variant: {variant!r}. Supported: {sorted(_HYDE_VARIANTS)}"
        )

    if variant == "paper":
        # 1) 가상 문서 생성
        hypo_doc = _generate_hypo_doc(state["user_query"])
        logger.debug("HyDE hypo_doc generated. length=%d", len(hypo_doc))

        hypo_text_hash = hashlib.md5(hypo_doc.encode()).hexdigest()[:8]
        search_query = hypo_doc
        hypo_used = True
    else:
        # subquery: 원본 질문으로 직접 검색
        search_query = state["user_query"]
        hypo_used = False
        hypo_text_hash = None

    # 2) 벡터 검색
    search_k = int(state.get("retrieval_k") or 3)
    search_results = _search_or_empty(db_korean, search_query, k=search_k)

    return {
        "search_results": search_results,
        "hyde_variant": variant,
        "hypo_used": hypo_used,
        "hypo_text_hash": hypo_text_hash,
    }


def generate_response(state: RAGState) -> RAGState:
    """답변 생성"""
    response_prompt = ChatPromptTemplate.from_template(
        "사용자 질문: {user_query}\n"
        "참고 문서: {search_results}\n\n"
        "위 문서를 근거로 질문에 답하세요. 답변은 한국어로 작성하세요."
    )
    response_chain = response_prompt | get_llm() | StrOutputParser()

    search_results = state["search_results"] or ["검색 결과가 없습니다."]
    final_answer = response_chain.invoke(
        {"user_query": state["user_query"], "search_results": search_results}
    )

    return {"final_answer": final_answer}


# 그래프 구성
builder = StateGraph(RAGState)
builder.add_node("hyde_search", hyde_search)
builder.add_node("generate_response", generate_response)

builder.add_edge(START, "hyde_search")
builder.add_edge("hyde_search", "generate_response")
builder.add_edge("generate_response", END)

graph = builder.compile()
