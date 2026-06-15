"""Step C: CandidateBundle 공통 인터페이스 테스트

KPI (REV_DECISION_STEP1 + Step C):
- CandidateBundle 스키마 필드 누락률 0%
- retrieve_candidates() → CandidateBundle 반환
- hyde paper 경로: hypo_used=True, hypo_text_hash 설정
- jaccard() 계산 정확도 검증
"""
from unittest.mock import MagicMock, patch

import pytest

import src.rag.graph as graph_module
from src.rag.candidates import CandidateBundle, jaccard, retrieve_candidates


# ── Red 1: CandidateBundle 스키마 필드 존재 ─────────────────────────────────
class TestCandidateBundleSchema:
    def test_has_mode_field(self):
        b = CandidateBundle(mode="hyde", query="q", candidates=[])
        assert b.mode == "hyde"

    def test_has_query_field(self):
        b = CandidateBundle(mode="hyde", query="테스트", candidates=[])
        assert b.query == "테스트"

    def test_has_candidates_field(self):
        b = CandidateBundle(mode="hyde", query="q", candidates=["doc1", "doc2"])
        assert b.candidates == ["doc1", "doc2"]

    def test_has_hyde_variant_default_none(self):
        b = CandidateBundle(mode="hyde", query="q", candidates=[])
        assert b.hyde_variant is None

    def test_has_hypo_used_default_false(self):
        b = CandidateBundle(mode="hyde", query="q", candidates=[])
        assert b.hypo_used is False

    def test_has_hypo_text_hash_default_none(self):
        b = CandidateBundle(mode="hyde", query="q", candidates=[])
        assert b.hypo_text_hash is None

    def test_has_metadata_default_empty_dict(self):
        b = CandidateBundle(mode="hyde", query="q", candidates=[])
        assert b.metadata == {}

    def test_metadata_is_independent_per_instance(self):
        """dataclass field(default_factory) — 공유 참조 버그 방지"""
        b1 = CandidateBundle(mode="hyde", query="q", candidates=[])
        b2 = CandidateBundle(mode="hyde", query="q", candidates=[])
        b1.metadata["key"] = "val"
        assert "key" not in b2.metadata


# ── Red 2: retrieve_candidates — hyde paper variant ──────────────────────────
FAKE_HYPO = "가상의 답변 문단입니다."
_PATCH_HYPO = "src.rag.graph._generate_hypo_doc"


@pytest.fixture(autouse=True)
def reset_graph_globals():
    graph_module.db_korean = MagicMock()
    graph_module.db_korean.similarity_search.return_value = []
    yield
    graph_module.db_korean = None
    graph_module.llm = None


class TestRetrieveCandidatesHydePaper:
    def test_returns_candidate_bundle(self):
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            result = retrieve_candidates("hyde", "질문", k=3)
        assert isinstance(result, CandidateBundle)

    def test_mode_is_hyde(self):
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            result = retrieve_candidates("hyde", "질문", k=3)
        assert result.mode == "hyde"

    def test_query_preserved(self):
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            result = retrieve_candidates("hyde", "원본 질문", k=3)
        assert result.query == "원본 질문"

    def test_paper_hypo_used_true(self):
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            result = retrieve_candidates("hyde", "질문", options={"hyde_variant": "paper"})
        assert result.hypo_used is True

    def test_paper_hypo_text_hash_set(self):
        import hashlib
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            result = retrieve_candidates("hyde", "질문", options={"hyde_variant": "paper"})
        expected = hashlib.md5(FAKE_HYPO.encode()).hexdigest()[:8]
        assert result.hypo_text_hash == expected

    def test_paper_hyde_variant_field_set(self):
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            result = retrieve_candidates("hyde", "질문", options={"hyde_variant": "paper"})
        assert result.hyde_variant == "paper"

    def test_default_variant_is_paper(self):
        """options 미지정 시 기본값 paper"""
        with patch(_PATCH_HYPO, return_value=FAKE_HYPO):
            result = retrieve_candidates("hyde", "질문")
        assert result.hypo_used is True


# ── Red 3: retrieve_candidates — hyde subquery variant ───────────────────────
class TestRetrieveCandidatesHydeSubquery:
    def test_subquery_hypo_used_false(self):
        result = retrieve_candidates("hyde", "질문", options={"hyde_variant": "subquery"})
        assert result.hypo_used is False

    def test_subquery_hypo_text_hash_none(self):
        result = retrieve_candidates("hyde", "질문", options={"hyde_variant": "subquery"})
        assert result.hypo_text_hash is None

    def test_subquery_hyde_variant_field(self):
        result = retrieve_candidates("hyde", "질문", options={"hyde_variant": "subquery"})
        assert result.hyde_variant == "subquery"

    def test_subquery_candidates_is_list(self):
        result = retrieve_candidates("hyde", "질문", options={"hyde_variant": "subquery"})
        assert isinstance(result.candidates, list)


# ── Red 4: jaccard() 계산 검증 ───────────────────────────────────────────────
class TestJaccard:
    def test_identical_lists(self):
        assert jaccard(["a", "b", "c"], ["a", "b", "c"]) == 1.0

    def test_disjoint_lists(self):
        assert jaccard(["a", "b"], ["c", "d"]) == 0.0

    def test_partial_overlap(self):
        # |{a,b} ∩ {b,c}| / |{a,b,c}| = 1/3
        assert abs(jaccard(["a", "b"], ["b", "c"]) - 1 / 3) < 1e-9

    def test_empty_both(self):
        assert jaccard([], []) == 1.0

    def test_one_empty(self):
        assert jaccard(["a"], []) == 0.0

    def test_duplicates_treated_as_set(self):
        """중복 항목은 집합으로 처리"""
        assert jaccard(["a", "a", "b"], ["a", "b"]) == 1.0

    def test_bundle_jaccard_usage(self):
        """CandidateBundle.candidates로 Jaccard 계산 패턴 검증"""
        b1 = CandidateBundle(mode="hyde", query="q", candidates=["x", "y", "z"])
        b2 = CandidateBundle(mode="hyde", query="q", candidates=["x", "y", "w"])
        score = jaccard(b1.candidates, b2.candidates)
        # |{x,y} ∩ {x,y,z,w}| = 2/4 = 0.5
        assert abs(score - 0.5) < 1e-9
