# RAG 관련 노트북 인덱스

- workspace: `/Users/jaehyuntak/Desktop/gangnam-1st/`
- 실행 환경: Python 3.13, `.venv/`, OpenAI API, Chroma `local_chroma_db/`

## RAG 핵심 노트북

| 노트북 | taxonomy | 경로 |
|--------|----------|------|
| `LLM_008_RAG_Evalution.ipynb` | [[RAG 평가 파이프라인]] | `/Users/jaehyuntak/Desktop/gangnam-1st/LLM_008_RAG_Evalution.ipynb` |
| `LLM_011_Query_Expansion.ipynb` | [[쿼리 확장 검색]] | `/Users/jaehyuntak/Desktop/gangnam-1st/LLM_011_Query_Expansion.ipynb` |
| `LLM_012_Rerank_Compression.ipynb` | [[압축 주입]] | `/Users/jaehyuntak/Desktop/gangnam-1st/LLM_012_Rerank_Compression.ipynb` |
| `LLM_013_Generation_Metrics_Me.ipynb` | [[RAG 평가 파이프라인]] | `/Users/jaehyuntak/Desktop/gangnam-1st/LLM_013_Generation_Metrics_Me.ipynb` |
| `LLM_025_LangGraph_SelfRAG.ipynb` | [[자기평가 검색]] | `/Users/jaehyuntak/Desktop/gangnam-1st/LLM_025_LangGraph_SelfRAG.ipynb` |
| `LLM_026_LangGraph_CRAG.ipynb` | [[교정 검색]] | `/Users/jaehyuntak/Desktop/gangnam-1st/LLM_026_LangGraph_CRAG.ipynb` |

## 벡터스토어 생성 근거

- 노트북: `LLM_013_Generation_Metrics_Me.ipynb`
- `persist_directory="./local_chroma_db"`
- `OpenAIEmbeddings(model="text-embedding-3-small")`
- 문서 수: 399개
- 데이터 소스: `blog total at 2025-03-31 merged_markdown.md`
- see_also: [[configs/rag.yaml]]
