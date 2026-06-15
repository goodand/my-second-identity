"""P0: HyDE variant 브랜칭 테스트

KPI (REV_DECISION_STEP1):
- hyde_variant, hypo_used, hypo_text_hash 누락률 0%
- paper variant 실행 시 hypo_doc 생성 100% 확인
"""
import hashlib
from unittest.mock import MagicMock, patch

import pytest

import src.rag.graph as graph_module
from src.rag.graph import hyde_search, RAGState


@pytest.fixture(autouse=True)
def reset_graph_globals():
    """각 테스트 전후 전역 상태 초기화"""
    graph_module.db_korean = MagicMock()
    graph_module.db_korean.similarity_search.return_value = []
    yield
    graph_module.db_korean = None
    graph_module.llm = None


def _make_state(**kwargs) -> RAGState:
    defaults = {
        "user_query": "테스트 질문",
        "search_results": [],
        "final_answer": "",
        "retrieval_k": 3,
        "hyde_variant": "paper",
        "hypo_used": False,
        "hypo_text_hash": None,
    }
    defaults.update(kwargs)
    return defaults  # type: ignore[return-value]


FAKE_HYPO = "가상의 답변 문단입니다."
_PATCH_HYPO = "src.rag.graph._generate_hypo_doc"


# ── Red 1: paper variant → hypo_doc 생성 후 검색 ────────────────────────────
class TestPaperVariant:
    def test_hypo_used_is_true(self):
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            state = _make_state(hyde_variant="paper")
            result = hyde_search(state)
        assert result["hypo_used"] is True, "paper variant는 hypo_used=True 이어야 한다"

    def test_hypo_text_hash_is_set(self):
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            state = _make_state(hyde_variant="paper")
            result = hyde_search(state)
        expected_hash = hashlib.md5(FAKE_HYPO.encode()).hexdigest()[:8]
        assert result["hypo_text_hash"] == expected_hash, \
            "paper variant는 hypo_text_hash를 MD5[:8]로 기록해야 한다"

    def test_resolved_variant_is_returned(self):
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            state = _make_state(hyde_variant="paper")
            result = hyde_search(state)
        assert result["hyde_variant"] == "paper"

    def test_search_uses_hypo_doc(self):
        """검색 쿼리가 원본 질문이 아닌 hypo_doc 이어야 한다"""
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            state = _make_state(hyde_variant="paper", user_query="원본 질문")
            hyde_search(state)
        call_args = graph_module.db_korean.similarity_search.call_args
        assert call_args[0][0] == FAKE_HYPO, \
            "paper variant는 hypo_doc으로 벡터 검색해야 한다"

    def test_search_uses_retrieval_k(self):
        """state.retrieval_k가 vector search k로 전달되어야 한다"""
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            state = _make_state(hyde_variant="paper", retrieval_k=7)
            hyde_search(state)
        call_args = graph_module.db_korean.similarity_search.call_args
        assert call_args.kwargs["k"] == 7


# ── Red 2: subquery variant → hypo_doc 생성 안 함 ───────────────────────────
class TestSubqueryVariant:
    def test_hypo_used_is_false(self):
        state = _make_state(hyde_variant="subquery")
        result = hyde_search(state)
        assert result["hypo_used"] is False, "subquery variant는 hypo_used=False 이어야 한다"

    def test_hypo_text_hash_is_none(self):
        state = _make_state(hyde_variant="subquery")
        result = hyde_search(state)
        assert result["hypo_text_hash"] is None, \
            "subquery variant는 hypo_text_hash가 None 이어야 한다"

    def test_resolved_variant_is_returned(self):
        state = _make_state(hyde_variant="subquery")
        result = hyde_search(state)
        assert result["hyde_variant"] == "subquery"

    def test_search_uses_original_query(self):
        state = _make_state(hyde_variant="subquery", user_query="원본 질문")
        hyde_search(state)
        call_args = graph_module.db_korean.similarity_search.call_args
        assert call_args[0][0] == "원본 질문", \
            "subquery variant는 원본 질문으로 벡터 검색해야 한다"

    def test_llm_not_called(self):
        with patch("src.rag.graph.get_llm") as mock_get_llm:
            state = _make_state(hyde_variant="subquery")
            hyde_search(state)
        mock_get_llm.assert_not_called()


# ── Red 3: 기본값은 paper ────────────────────────────────────────────────────
class TestDefaultVariant:
    def test_default_is_paper(self):
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            state = _make_state()
            state.pop("hyde_variant", None)  # type: ignore[misc]
            result = hyde_search(state)
        assert result["hypo_used"] is True, "기본 variant는 paper(hypo_used=True)여야 한다"
        assert result["hyde_variant"] == "paper"


class TestInvalidVariant:
    def test_unknown_variant_raises(self):
        state = _make_state(hyde_variant="papre")
        with pytest.raises(ValueError, match="Unsupported hyde_variant"):
            hyde_search(state)


# ── Red 4: RAGState 필드 존재 확인 ──────────────────────────────────────────
class TestRAGStateFields:
    def test_state_has_hyde_variant_field(self):
        annotations = RAGState.__annotations__
        assert "hyde_variant" in annotations, "RAGState에 hyde_variant 필드가 있어야 한다"

    def test_state_has_hypo_used_field(self):
        assert "hypo_used" in RAGState.__annotations__, \
            "RAGState에 hypo_used 필드가 있어야 한다"

    def test_state_has_hypo_text_hash_field(self):
        assert "hypo_text_hash" in RAGState.__annotations__, \
            "RAGState에 hypo_text_hash 필드가 있어야 한다"

    def test_state_has_retrieval_k_field(self):
        assert "retrieval_k" in RAGState.__annotations__, \
            "RAGState에 retrieval_k 필드가 있어야 한다"
