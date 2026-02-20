# RAG Performance Upgrade Plan

- ver: `v1.2.0`
- target_workspace: `gangnam-1st (active workspace)`
- source_context: `gangnam-1st` notebooks + `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`

## Review Remediation Status
- `DONE` 논문 #02(Lost in the Middle) 오서술 pseudocode 수정: 진단형 실험 절차로 교체.
- `DONE` 다이어그램 #03(Multi-Query) orphan edge 수정: `R1 -> RF`, `R2 -> RF` 반영.
- `DONE` HyDE 다이어그램에 `Embedding/Similarity Search` 단계 명시.
- `DONE` `src/graph.py` 런타임 블로커 수정: `db_korean/db_english` 미정의로 인한 즉시 실패 제거.
- `DONE` `src/graph.py` import-time LLM 초기화 제거: `configure_llm()/get_llm()` 지연 초기화 적용.
- `DONE` `src/graph.py` 검색 예외 처리 보강: vector store 미설정/검색 실패 시 warning/exception 로그 추가.
- `DONE` 다이어그램 #05(Query Decomposition) Mermaid 파서 오류 수정: `()` 레이블에 따옴표 추가.
- `DONE` 다이어그램 #04(HyDE) 중복 Retriever 노드 제거: Similarity Search → Retrieved Documents로 단축.
- `DONE` KB #07 Self-RAG PDF 중복 항목 → FiD(2007.01282)로 교체.
- `DONE` KB #01 HyDE pseudocode 3번 줄: "필요 시 q" 오서술 수정.
- `DONE` 다이어그램 #02 adjacency_list에 Write/Read 독립 경로 주석 추가.
- `OPEN` 비밀정보 정리/키 로테이션(.env, .history, 노트북 셀)은 별도 보안 작업으로 진행 필요.
- `OPEN` 실행 코드 아티팩트(`src/eval`, `configs`, `scripts`)는 Phase 1~2에서 우선 구현 필요.
- `OPEN` `src/graph.py` `graph = builder.compile()` 모듈 레벨 실행 → `build_graph()` 팩토리 패턴으로 분리 (langgraph.json 호환성 확인 후 진행).

## Document Map

| 문서 | 역할 | 링크 |
|------|------|------|
| `PLAN.md` (이 파일) | 실행 계획 · 단계 · 에이전트 운영 규칙 | — |
| `RAG_URL_KNOWLEDGE_BASE.md` | 논문 8편 + 참고 URL 33개 — 실험 티켓 단일 레퍼런스 | [→](RAG_URL_KNOWLEDGE_BASE.md) |
| `IMAGE_STRUCTURE_GRAPHS.md` | 8개 RAG 아키텍처 다이어그램 + adjacency_list | [→](IMAGE_STRUCTURE_GRAPHS.md) |
| `IMAGE_URL_MATCHES.md` | 이미지 URL ↔ 노트북/KB 소스 매핑 (22 URLs, 8 matched) | [→](IMAGE_URL_MATCHES.md) |
| `../codex/MASTER_SUMMARY.md` | 워크스페이스 전체 P0/P1/P2 리스크 진단 | [→](../codex/MASTER_SUMMARY.md) |

**추천 읽기 순서:** PLAN.md → [KB](RAG_URL_KNOWLEDGE_BASE.md) (실험 근거) → [Diagrams](IMAGE_STRUCTURE_GRAPHS.md) (시각 구조) → [MASTER_SUMMARY](../codex/MASTER_SUMMARY.md) (운영 리스크)

> 토큰이 큰 작업(논문 본문 취합)은 KB에서 우선순위를 고른 뒤, 8에이전트 병렬 요약으로 별도 실행한다.

## Objective
RAG 시스템을 실험형 노트북 단계에서 운영 가능한 평가-개선 루프 단계로 전환한다.

## Success Criteria
- 정량 목표: 기준선 대비 핵심 지표 개선 (`Faithfulness`, `Answer Relevance`, `Context Precision/Recall`, `Latency`, `Cost`).
- 안정성 목표: 동일 데이터셋 재실행 시 결과 변동 허용범위 내 유지.
- 운영성 목표: 오프라인 평가 + 온라인 샘플 평가 자동 실행.

## Execution Phases
1. Baseline and Reproducibility
- 워크스페이스 구조: `src/rag/`, `src/eval/`, `configs/`, `datasets/`, `artifacts/`, `plans/`
- 데이터셋 표준화: `evaluation_dataset`, `synthetic_testset_revised`, `ragas_evaluation_results`
- 베이스라인 스냅샷 고정 (청킹/임베딩/리트리버/프롬프트/모델)
- see_also: 논문 [#06 RAG 기초 공식화](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · 운영 리스크 [MASTER_SUMMARY §P1](../codex/MASTER_SUMMARY.md#p1-이번-주)

2. Evaluation Harness
- 휴리스틱 + ROUGE/BLEU + String/Embedding distance + LLM-as-Judge + RAGAS 통합
- Hard fail + 품질 임계치 + 비용/지연 임계치 게이트 설정
- 슬라이스 리포트(질문유형/길이/도메인)
- see_also: 논문 [#04 RAG Survey](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · [#02 Lost in the Middle](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · 다이어그램 [#08 평가 파이프라인](IMAGE_STRUCTURE_GRAPHS.md#08-rag-evaluationbenchmark-pipeline)

3. Retrieval Improvement
- 인덱싱 실험: chunk size/overlap, metadata filter, multi-vector
- 검색 전략 실험: [[쿼리 확장 검색]] (query rewrite · multi-query · HyDE · hybrid) · [[교정 검색]] (CRAG) · [[자기평가 검색]] (Self-RAG)
- 컨텍스트 최적화: [[압축 주입]] (compression/rerank) + 토큰 예산 제어
- see_also: 논문 [#01 HyDE](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · [#05 DMQR-RAG](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · 다이어그램 [#03 Multi-Query](IMAGE_STRUCTURE_GRAPHS.md#03-multi-query--rag-fusion--dmqr-rag) · [#04 HyDE](IMAGE_STRUCTURE_GRAPHS.md#04-hyde) · [#05–07](IMAGE_STRUCTURE_GRAPHS.md#05-query-decomposition)

4. Generation Improvement
- [[근거 강제 주입]] (grounded prompt · citation policy · abstention policy)
- 모델 라우팅(품질/비용 곡선 기반)
- 실패 taxonomy(hallucination/irrelevant/omission) 기반 개선
- see_also: 논문 [#03 Self-RAG](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · [#07 FiD](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · [#08 CRAG](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls)

5. Ops and Continuous Improvement
- CI: PR마다 오프라인 평가 + baseline delta 검사
- 온라인: trace 샘플링 + 주간 리포트
- 릴리즈: 평가 통과 시 배포, 회귀 시 롤백
- see_also: [MASTER_SUMMARY §P2](../codex/MASTER_SUMMARY.md#p2-다음-스프린트)

## 8-Agent Operation Plan
- A01: Query expansion/HyDE/MultiQuery 개선 트랙 · see_also: KB [#01](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) [#05](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · Diagrams [#03](IMAGE_STRUCTURE_GRAPHS.md#03-multi-query--rag-fusion--dmqr-rag) [#04](IMAGE_STRUCTURE_GRAPHS.md#04-hyde) [#05](IMAGE_STRUCTURE_GRAPHS.md#05-query-decomposition) [#06](IMAGE_STRUCTURE_GRAPHS.md#06-query-rewrite-trainable-rewrite-retrieve-read) [#07](IMAGE_STRUCTURE_GRAPHS.md#07-step-back-prompting)
- A02: Evaluation 지표/벤치마크 트랙 · see_also: KB [#04](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) [#02](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls) · Diagram [#08](IMAGE_STRUCTURE_GRAPHS.md#08-rag-evaluationbenchmark-pipeline)
- A03: Rerank/Compression 트랙 · see_also: KB [#07 FiD](RAG_URL_KNOWLEDGE_BASE.md#paper-like-urls)
- A04: LangGraph/Memory 트랙 · see_also: Diagram [#02 Short/Long Memory](IMAGE_STRUCTURE_GRAPHS.md#02-short-vs-long-memory-recovered)
- A05: 도메인 데이터 소스 트랙 · see_also: KB [Other URLs §ETF](RAG_URL_KNOWLEDGE_BASE.md#other-rag-references-urls)
- A06: 멀티모달/반정형 트랙 · see_also: Diagram [#01 CLIP](IMAGE_STRUCTURE_GRAPHS.md#01-clip-contrastive-pre-training)
- A07: Tooling/SDK/LangSmith 트랙 · see_also: KB [Other URLs §LangSmith](RAG_URL_KNOWLEDGE_BASE.md#other-rag-references-urls)
- A08: 통합 검수(중복/포맷/노이즈 제거) · see_also: [IMAGE_URL_MATCHES.md](IMAGE_URL_MATCHES.md)

### Protocol
1. URL shard 분할: `plans/rag-upgrade/agents/urls-agent-0X.txt`
2. 병렬 실행: `- [한 줄 설명](URL)` 형식 강제
3. 병합: 단일 기준 문서 `RAG_URL_KNOWLEDGE_BASE.md` 업데이트
4. 검수: 중복/깨진 링크/의미 없는 설명 제거
5. 버전 규칙: `major` 구조 변경, `minor` 분류 추가, `patch` 링크/오탈자

## Backlog Source
- `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`를 실험 티켓의 단일 레퍼런스로 사용
