# MASTER_SUMMARY

- ver: `v1.0.0`
- generated_at: `2026-02-19`
- codex_cli: `0.104.0`
- sources:
  - `plans/codex/research/agent-01.md`
  - `plans/codex/research/agent-02.md`
  - `plans/codex/research/agent-03.md`
  - `plans/codex/research/agent-04.md`
  - `plans/codex/research/agent-05.md`
  - `plans/codex/research/agent-06.md`
  - `plans/codex/research/agent-07.md`
  - `plans/codex/research/agent-08.md`

## Document Map

| 문서 | 역할 |
|------|------|
| `MASTER_SUMMARY.md` (이 파일) | 워크스페이스 전체 P0/P1/P2 리스크 진단 |
| [DECISION_DESIGN_SPEC_v1.md](DECISION_DESIGN_SPEC_v1.md) | RAG 성능 최적화 실험의 의사결정/설계 원칙 고정본 |
| [PLAN.md](../../../gemini/PLAN.md) | RAG 업그레이드 실행 계획 · 5단계 · 8에이전트 |
| [RAG_URL_KNOWLEDGE_BASE.md](../knowledge/RAG_URL_KNOWLEDGE_BASE.md) | 논문 19편 + 참고 URL 33개 인덱스 |
| [IMAGE_STRUCTURE_GRAPHS.md](../../../gemini/IMAGE_STRUCTURE_GRAPHS.md) | RAG 아키텍처 다이어그램 8개 |
| [agent-06.md](../../research/agent-06.md) | Generation Metrics 다음 작업 — Evaluation Harness 설계 근거 |

## One-line Summary
학습용 노트북 중심 워크스페이스에 `src/`, `depsolve_ext`, `mcp-test`, `docker-elk-main`이 혼재되어 있고, 현재 최우선 리스크는 비밀정보 노출/환경 분산/런타임 결손(`db_korean`, `db_english`)입니다.

## P0 (즉시)
1. 비밀정보 정리 및 키 로테이션
- 대상: `.env`, `.history/.env_*`, `agent-made-by-gemini.py`, `LLM_013_Generation_Metrics_Me.ipynb`, `review-agent-2026.ipynb`, `plans/codex/*.run.log`
- see_also: [PLAN.md §Remediation Status `OPEN` 보안 항목](../../../gemini/PLAN.md#review-remediation-status)

2. 런타임 치명 결손 수정
- 대상: `src/graph.py` (`db_korean`, `db_english` 초기화/주입)
- see_also: [PLAN.md §Remediation Status `DONE` graph.py 항목](../../../gemini/PLAN.md#review-remediation-status) _(완료됨)_

3. ELK insecure 기본값 차단
- 대상: `docker-elk-main/elasticsearch/config/elasticsearch.yml`, `docker-elk-main/.env`, `docker-elk-main/extensions/fleet/*.yml`

## P1 (이번 주)
1. 의존성 단일화
- 대상: `pyproject.toml`, `pyproject.docling.toml`, `requirements.txt`, `mcp-test/requirements.txt`
- see_also: [PLAN.md Phase 1 베이스라인](../../../gemini/PLAN.md#execution-phases)

2. 루트 거버넌스 정리
- 루트 Git/README 기준 확정, `mcp-test/.git` 분리/병합 정책 결정

3. 예외/관측 가능성 보강
- 대상: `depsolve_ext/analyzer.py`, `depsolve_ext/extensions.py`, `depsolve_ext/cli.py`, `mcp-test/weather_server*.py`

## P2 (다음 스프린트)
1. 노트북-프로덕션 경계 확정 및 통합
- 대상: `LLM_013_Generation_Metrics*.ipynb` 포함 중복 노트북 정리
- see_also: [PLAN.md Phase 1 베이스라인](../../../gemini/PLAN.md#execution-phases)

2. 생성평가 파이프라인 모듈화
- 제안 대상: `src/eval/generation_metrics.py`, `src/eval/run_offline_eval.py`, `src/eval/run_online_eval.py`, `configs/eval/generation_eval.yaml`
- see_also: [PLAN.md Phase 2 평가 하네스](../../../gemini/PLAN.md#execution-phases) · [KB #04 RAG Survey](../knowledge/RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · [Diagram #08 평가 파이프라인](../../../gemini/IMAGE_STRUCTURE_GRAPHS.md#08-rag-evaluationbenchmark-pipeline)

3. 데이터 거버넌스 정책 수립
- 대상: `data/` 전반 (`membership`, `creditcard`, `sqlite-sakila.db` 등)

## Evaluation Hint 반영 (LLM_013_Generation_Metrics_Me.ipynb)
이미 구현된 축:
- 휴리스틱, ROUGE/BLEU, 문자열 거리, 임베딩 거리, LangSmith 평가 패턴

부족한 축:
- 기준선/게이트(합격선), 슬라이스 리포트, 회귀 자동화(CI), 재현성 스키마
- see_also: [PLAN.md Phase 2 평가 하네스 §OPEN](../../../gemini/PLAN.md#review-remediation-status) · [KB #04 RAG Survey](../knowledge/RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls)

즉시 권장:
1. 오프라인 게이트 정의(하드 fail + 품질 delta)
2. 온라인 샘플링 + human review 큐
3. 평가 결과 baseline snapshot 관리

## Agent Deliverables
- `plans/codex/research/agent-01.md`: 구조/아키텍처
- `plans/codex/research/agent-02.md`: Python 런타임/보안 리스크
- `plans/codex/research/agent-03.md`: `depsolve_ext` 심층 진단
- `plans/codex/research/agent-04.md`: MCP 운영 준비도
- `plans/codex/research/agent-05.md`: 노트북 생태계/재현성
- `plans/codex/research/agent-06.md`: Generation Metrics 다음 작업
- `plans/codex/research/agent-07.md`: 데이터/인프라/환경 리스크
- `plans/codex/research/agent-08.md`: 경영 요약/30-60-90 로드맵
