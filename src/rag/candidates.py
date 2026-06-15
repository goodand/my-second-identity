"""Step C: CandidateBundle 공통 인터페이스

서비스 코드베이스(src/rag/graph.py)와 실험 코드베이스(plans/codex/algorithms/)를
통합하는 공통 스키마 및 검색 진입점.

KB #01 HyDE + REV_DECISION_STEP1 provenance 필드 포함.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CandidateBundle:
    """검색 결과 + 실행 증적(provenance)을 담는 공통 컨테이너.

    Attributes:
        mode: 검색 모드 식별자 (예: "hyde", "sequential_parent_child", ...)
        query: 원본 사용자 질의
        candidates: 검색된 청크 텍스트 목록 (top-k)
        hyde_variant: HyDE 분기 ("paper" | "subquery"), 비 HyDE 모드는 None
        hypo_used: paper variant 실행 시 True (hypo_doc로 검색)
        hypo_text_hash: hypo_doc MD5[:8], provenance 추적용 (REV_DECISION_STEP1 KPI)
        metadata: 추가 실행 메타데이터 (latency, k값 등)
    """
    mode: str
    query: str
    candidates: List[str]
    hyde_variant: Optional[str] = None
    hypo_used: bool = False
    hypo_text_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def jaccard(a: List[str], b: List[str]) -> float:
    """두 후보 리스트의 Jaccard 유사도 (집합 기준).

    KPI 검증용: hyde vs A3 Jaccard <= 0.70 (REV_DECISION_STEP1).

    Args:
        a: 첫 번째 후보 텍스트 목록
        b: 두 번째 후보 텍스트 목록

    Returns:
        0.0 ~ 1.0 범위의 Jaccard 유사도
    """
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def retrieve_candidates(
    mode: str,
    query: str,
    k: int = 3,
    options: Optional[Dict[str, Any]] = None,
) -> CandidateBundle:
    """서비스 코드베이스의 통합 검색 진입점.

    Args:
        mode: 검색 모드 ("hyde" 지원; 추가 모드는 Step D에서 확장)
        query: 사용자 질의
        k: 반환할 최대 후보 수
        options: 모드별 추가 옵션
            - hyde_variant: "paper" (기본) | "subquery"

    Returns:
        CandidateBundle with provenance fields

    Raises:
        ValueError: 지원하지 않는 mode 지정 시
    """
    from src.rag import graph as graph_module

    opts = options or {}

    if mode == "hyde":
        hyde_variant = opts.get("hyde_variant", "paper")
        state = {
            "user_query": query,
            "search_results": [],
            "final_answer": "",
            "retrieval_k": k,
            "hyde_variant": hyde_variant,
            "hypo_used": False,
            "hypo_text_hash": None,
        }
        result = graph_module.hyde_search(state)
        return CandidateBundle(
            mode=mode,
            query=query,
            candidates=result.get("search_results", []),
            hyde_variant=result.get("hyde_variant"),
            hypo_used=result.get("hypo_used", False),
            hypo_text_hash=result.get("hypo_text_hash"),
            metadata={"k": k},
        )

    raise ValueError(f"Unsupported mode: {mode!r}. Supported: ['hyde']")
