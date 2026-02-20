# AGENT_INSTRUCTIONS.md

> 새 세션에서 이 프로젝트를 이어받는 에이전트를 위한 지침서.
> 이 파일을 먼저 읽고, 그 다음 `plans/PLAN.md` → `plans/RAG_URL_KNOWLEDGE_BASE.md` 순으로 읽어라.

---

## 1. 프로젝트 정체성

**이름:** `my-second-identity`
**목적:** 개인 블로그 데이터 기반 한국어 RAG 시스템 — 실험형 노트북에서 운영 가능한 평가-개선 루프로 전환
**핵심 의도:** "효과적인 컨텍스트 주입"

이 프로젝트는 `/Users/jaehyuntak/Desktop/gangnam-1st/` 워크스페이스에서 분리·정제된 것이다.
gangnam-1st는 학습 노트북 혼재 환경이었고, 이 repo는 그것의 RAG 핵심만 추출한 클린 버전이다.

---

## 2. 현재 상태 (Phase 위치)

```
Phase 1: Baseline & Reproducibility     ← 미완 (eval dataset 없음)
Phase 2: Evaluation Harness             ← 미시작 (src/eval/ 비어 있음)
Phase 3: Retrieval Improvement          ← 진입점 완료 (HyDE 구현됨)
Phase 4: Generation Improvement        ← 미시작
Phase 5: Ops & CI                       ← 미시작
```

**현재 코드 위치:** Phase 3 진입점 (`쿼리 확장 검색 × 비정제 주입`)

---

## 3. 디렉토리 구조 및 각 파일 역할

```
my-second-identity/
├── src/
│   ├── rag/
│   │   ├── graph.py          핵심 LangGraph RAG 파이프라인
│   │   └── bootstrap.py      Chroma → graph.py 연결 진입점 (중요)
│   └── eval/                 비어 있음 — Phase 2에서 구현
├── configs/
│   └── rag.yaml              vector store 경로, 임베딩 모델 명세
├── datasets/                 비어 있음 — Phase 1에서 eval_v0.jsonl 생성
├── plans/
│   ├── PLAN.md               5단계 실행 계획 + 8에이전트 운영 규칙
│   ├── RAG_URL_KNOWLEDGE_BASE.md   논문 8편 (pseudocode_3lines 포함)
│   ├── IMAGE_STRUCTURE_GRAPHS.md  RAG 아키텍처 다이어그램 8개 (Mermaid)
│   ├── IMAGE_URL_MATCHES.md       이미지 URL ↔ 노트북 소스 매핑
│   ├── notebooks.md               RAG 노트북 path/backlink 인덱스
│   ├── codex/
│   │   ├── MASTER_SUMMARY.md      P0/P1/P2 리스크 진단
│   │   └── agent-01~08.md         gangnam-1st 워크스페이스 심층 분석
│   └── claude/
│       └── AGENT_INSTRUCTIONS.md  ← 이 파일
├── pyproject.toml
├── .env.example
└── .gitignore
```

---

## 4. 벡터스토어 (절대 경로)

```yaml
# configs/rag.yaml
persist_directory: /Users/jaehyuntak/Desktop/gangnam-1st/local_chroma_db
embedding_model: text-embedding-3-small
language: korean
```

- **문서 수:** 399개
- **데이터 소스:** 개인 블로그 merged_markdown (fetp.tistory.com 포함)
- **생성 노트북:** `/Users/jaehyuntak/Desktop/gangnam-1st/LLM_013_Generation_Metrics_Me.ipynb`
- **주의:** 이 경로는 로컬 절대경로다. 머신이 바뀌면 `configs/rag.yaml`의 `persist_directory`를 수정해야 한다.

---

## 5. 실행 방법

### 환경 설정
```bash
cd my-second-identity
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env   # OPENAI_API_KEY 입력
```

### RAG 실행 (bootstrap → graph)
```python
from src.rag.bootstrap import bootstrap
from src.rag.graph import graph

bootstrap()  # Chroma → configure_vectorstore() 주입
result = graph.invoke({"user_query": "질문을 여기에"})
print(result["final_answer"])
```

### 직접 실행 (테스트)
```bash
python -m src.rag.bootstrap
```

---

## 6. 핵심 아키텍처 결정사항

### 6-1. graph.py 설계 원칙
- **언어 판별 노드 제거:** 한국어 전용이므로 `analyze_input` 불필요
- **HyDE 적용:** `hyde_search` 노드가 원 쿼리 대신 가상 문서로 검색
- **State 스키마:** `RAGState` (user_query, search_results, final_answer)
- **db_english 제거:** 한국어 벡터스토어만 사용

### 6-2. bootstrap.py의 역할 (gangnam-1st에서 식별된 gap 해소)
gangnam-1st에서 발견된 구조적 문제:
- `local_chroma_db` 아티팩트 존재 ✓
- `graph.py`의 `configure_vectorstore()` 인터페이스 존재 ✓
- **두 개를 연결하는 코드가 없었음 ✗**

`bootstrap.py`가 이 gap을 메운다. 앱 시작 시 반드시 `bootstrap()` 호출 필요.

### 6-3. HyDE 구현 근거
- **KB #01:** `arxiv.org/abs/2212.10496`
- **핵심:** 원 쿼리 임베딩 대신 LLM이 생성한 가상 문서를 임베딩해 검색
- **pseudocode:**
  1. q → LLM → 가상 문서 d_hypo 생성
  2. d_hypo → embedding → similarity_search → top-k
  3. top-k를 컨텍스트로 답변 생성

---

## 7. taxonomy (컨텍스트 주입 전략)

이 프로젝트의 개발 방향을 이해하는 핵심 개념 지도.

**Axis A: 검색 범위·품질**
| 종 | 조건 | 관련 KB | 현재 상태 |
|----|------|---------|----------|
| [[단일 벡터 검색]] | q → embedding → top-k | KB #06 | baseline (삭제됨) |
| [[쿼리 확장 검색]] | HyDE/Multi-Query → 다양성 확장 | KB #01 #05 | **현재 구현** |
| [[교정 검색]] | CRAG → quality-check → filtered | KB #08 | Phase 4 |
| [[자기평가 검색]] | Self-RAG → 검색 필요 여부 판단 | KB #03 | Phase 4 |

**Axis B: 주입 정제 수준**
| 종 | 조건 | 관련 KB | 현재 상태 |
|----|------|---------|----------|
| [[비정제 주입]] | raw top-k concat | — | **현재 구현** |
| [[위치 인식 주입]] | 근거를 앞·뒤 배치, U자형 방지 | KB #02 | Phase 3 후반 |
| [[압축 주입]] | rerank → 압축된 핵심 세그먼트 | KB #07 #04 | Phase 3 후반 |
| [[근거 강제 주입]] | citation policy + abstention | — (KB 없음) | Phase 4 |

**현재 위치:** `[[쿼리 확장 검색]] × [[비정제 주입]]`
**목표:** `[[쿼리 확장 검색]] × [[압축 주입]]`

---

## 8. 다음 작업 우선순위

### 즉시 (Phase 1 완료 조건)
1. **평가 데이터셋 생성** — `datasets/eval_v0.jsonl` (30~50개 Q&A)
   - 벡터스토어의 블로그 문서 기반으로 질의-답변 쌍 생성
   - 형식: `{"query": "...", "ground_truth": "...", "context": ["..."]}`
2. **baseline 측정** — 현재 HyDE 파이프라인의 점수 스냅샷 저장
   - 지표: Faithfulness, Answer Relevance, Context Precision/Recall

### 이번 주 (Phase 2)
3. **`src/eval/` 구현** — `generation_metrics.py`, `run_offline_eval.py`
   - RAGAS 또는 LangSmith evaluator 사용
   - KB #04 RAG Survey의 pseudocode 참조

### 다음 (Phase 3 후반)
4. **Axis B 개선** — `[[압축 주입]]` 구현
   - `LLM_012_Rerank_Compression.ipynb` 참조 (gangnam-1st)
   - KB #07 FiD pseudocode 참조

---

## 9. 참조해야 할 노트북 (gangnam-1st)

| 노트북 | 필요한 순간 |
|--------|------------|
| `LLM_013_Generation_Metrics_Me.ipynb` | 벡터스토어 재생성, 평가 패턴 참조 |
| `LLM_011_Query_Expansion.ipynb` | HyDE/Multi-Query 구현 참조 |
| `LLM_012_Rerank_Compression.ipynb` | 압축 주입 구현 시 |
| `LLM_025_LangGraph_SelfRAG.ipynb` | Self-RAG 구현 시 |
| `LLM_026_LangGraph_CRAG.ipynb` | CRAG 구현 시 |

경로: `/Users/jaehyuntak/Desktop/gangnam-1st/[노트북명]`

---

## 10. 금지 사항 / 주의사항

- **`graph = builder.compile()`** 은 모듈 레벨에 있음. 이것을 `build_graph()` 팩토리로 바꾸려면 `langgraph.json` 호환성 먼저 확인 필요.
- **벡터스토어 경로**는 절대경로. 복사/이동 시 `configs/rag.yaml` 업데이트 필수.
- **`bootstrap()` 미호출 시** `db_korean=None`이므로 `_search_or_empty`가 항상 `[]` 반환.
- **평가 데이터셋**(`datasets/`)은 `.gitignore`에 포함됨 — 의도적. 민감 데이터 포함 가능성 때문.
- **`db_english`는 제거됨** — 한국어 전용 설계.

---

## 11. 기술 스택

```toml
langgraph          # LangGraph StateGraph
langchain-openai   # ChatOpenAI, OpenAIEmbeddings
langchain-chroma   # Chroma 벡터스토어
python-dotenv      # .env 로드
pyyaml             # configs/rag.yaml 파싱
```

LLM 기본값: `gpt-4.1-mini` (configs/rag.yaml의 `llm.model`로 변경 가능)

---

## 12. 이 파일을 읽은 후 해야 할 일

1. `plans/PLAN.md` 읽기 — 5단계 전체 맥락 확인
2. `plans/RAG_URL_KNOWLEDGE_BASE.md` 읽기 — 구현할 기법의 pseudocode 확인
3. `src/rag/graph.py`와 `src/rag/bootstrap.py` 읽기 — 현재 코드 파악
4. **섹션 8의 다음 작업 우선순위**에서 가장 위 항목부터 시작
