## Scope
- Analyzed all `*.ipynb` found under repo: `68` total.
- First-party notebooks (excluding `.history` and virtualenv site-packages): `59`.
- Non-project notebook copies included in scan:
  - `.history/*` (`7`) including one broken JSON notebook: `.history/LLM_013_Generation_Metrics_Me_20260108163553.ipynb`
  - `.venv/.../density_relevance.ipynb` and `.venv-docling/.../density_relevance.ipynb`
- Repo distribution:
  - Root notebooks: `54`
  - `Module01_파이썬/`: `3`
  - `dacon/`: `1`
  - `elk/`: `1`

## Notebook clusters by topic
- LLM stack (`36`): strong concentration in RAG/LangGraph/eval workflows.
  - RAG/retrieval examples: `LLM_004_LangChain_PDF_RAG.ipynb`, `LLM_010_Hybrid_Search.ipynb`, `LLM_012_Rerank_Compression.ipynb`, `LLM_031_Multimodal_RAG_Part1[Answer].ipynb`
  - LangGraph flow examples: `LLM_019_LangGraph_StateGraph.ipynb`, `LLM_022_LangGraph_Memory.ipynb`, `LLM_026_LangGraph_CRAG.ipynb`
  - Evaluation/observability examples: `LLM_013_Generation_Metrics.ipynb`, `LLM_014_LLM-as-Judge-LangChain.ipynb`, `LLM_015_Langfuse_Evaluation.ipynb`
- ML/competition (`8`): Kaggle/Dacon and baseline modeling.
  - `ML_01_Kaggle_Housing_Prices.ipynb`, `[Dacon]_001_EDA.ipynb`, `dacon/[Baseline_Train]_LightGBM을 활용한 모델 학습 및 피쳐엔지니어링 (학습).ipynb`
- Data engineering/analytics (`4`): crawling/API/visualization.
  - `DS_004_Visualization[Lecture].ipynb`, `DS_007_crawl4ai.ipynb`
- TensorFlow (`3`): tutorial-to-colab style.
  - `TF_01_basic.ipynb`, `TF_04_Tensorflow_Classification_Colab.ipynb`
- Python basics (`4`): lecture material.
  - `Module01_파이썬/001_...ipynb`, `pandas.ipynb`
- Infra/graph DB (`1` + LLM graph notebooks): `elk/elk_intro.ipynb`, plus `LLM_034_neo4j_intro.ipynb`, `LLM_036_neo4j_Structred_ETF.ipynb`

## Duplication/maintenance risks
- Version sprawl in history snapshots for same notebook:
  - `.history/LLM_013_Generation_Metrics_Me_20260108163112.ipynb` ... `.history/LLM_013_Generation_Metrics_Me_20260108165840.ipynb`
- Vendored notebooks duplicated across virtualenvs:
  - `.venv/lib/python3.13/site-packages/chromadb/experimental/density_relevance.ipynb`
  - `.venv-docling/lib/python3.13/site-packages/chromadb/experimental/density_relevance.ipynb`
- Parallel “answer/variant” notebooks increase drift risk:
  - `LLM_013_Generation_Metrics.ipynb` vs `LLM_013_Generation_Metrics_Me.ipynb`
  - `LLM_031_Multimodal_RAG_Part1[Answer].ipynb` and `LLM_032_Multimodal_RAG_Part2[Answer].ipynb`
- Output-heavy notebooks likely to create noisy diffs and merge pain (examples):
  - `[시계열]_001_...ipynb` (`80/81` code cells with outputs)
  - `DS_004_Visualization[Lecture].ipynb` (`51/57`)
  - `LLM_004_LangChain_PDF_RAG.ipynb` (`50/65`)
- Large notebook artifacts (likely embedded outputs/assets):
  - `LLM_027_Unstructured_Docling.ipynb` (`4.6M`)
  - `ML_02_Mebership_classification.ipynb` (`2.0M`)
  - `LLM_029_Multimodal_LangChain_CLIP.ipynb` (`1.7M`)

## Reproducibility risks (env/data/dependency)
- Python/runtime fragmentation across notebooks:
  - Kernels report `3.13.6`, `3.12.12`, `3.12.11`, `3.11.11`, `3.13.2`, `3.9.6` (e.g., `test.ipynb` on `3.9.6`)
- First-party notebooks with zero executed code cells (unverified state):
  - `LLM_015_Langfuse_Evaluation.ipynb`, `LLM_028_Unstructured_Docling_RAG_10-K.ipynb`, `LLM_040_GraphRAG_Hybrid_Implementation.ipynb`
- Absolute local path coupling (machine-specific):
  - `LLM_013_Generation_Metrics_Me.ipynb` (`/Users/jaehyuntak/Desktop/...`)
  - `LLM_023_LangGraph_HITL.ipynb` (`/Users/jaehyuntak/Downloads/IMG_9544.JPG`)
  - `review-agent-2026.ipynb` absolute file/data paths
- External service and secret dependency without standardized bootstrap:
  - `LLM_001_Langchain_Components.ipynb`, `LLM_004_LangChain_PDF_RAG.ipynb` (`OPENAI_API_KEY` usage patterns)
  - `DS_007_crawl4ai.ipynb` runtime failure requiring `playwright install`
- Dependency capture gap between notebooks and manifests:
  - `requirements.txt` is minimal (`mcp[cli]`, `uvicorn`) vs broad notebook imports (`langchain_*`, `sklearn`, `tensorflow`, `crawl4ai`, `ranx`, etc.)
- In-notebook ad-hoc install instructions:
  - `LLM_009_Retrieval_Metrics.ipynb` (`!pip install ranx`)
  - `elk/elk_intro.ipynb` (`!pip install elasticsearch`)

## Suggested consolidation plan
- Define notebook boundary and ignore policy:
  - Keep only first-party notebooks; exclude `.history/**` and `.venv*/**` from notebook governance and reviews.
- Consolidate into track folders with canonical notebooks:
  - `notebooks/llm/rag/`, `notebooks/llm/langgraph/`, `notebooks/llm/eval/`, `notebooks/ml/`, `notebooks/ds/`, `notebooks/tf/`
  - Promote one canonical file per topic and archive variants (example: keep one of `LLM_013_Generation_Metrics*.ipynb`).
- Standardize reproducible execution contract:
  - One pinned environment path (`pyproject.toml` + `uv.lock`) covering notebook dependencies; align/remove conflicting `pyproject.docling.toml` split only if truly needed.
  - Add a shared bootstrap cell template (`env check`, key presence checks, deterministic seed, relative data root).
- Remove machine-specific coupling:
  - Replace absolute paths with project-relative `Path` usage (`data/...`) in notebooks like `LLM_013_Generation_Metrics_Me.ipynb`, `LLM_023_LangGraph_HITL.ipynb`.
- Reduce notebook diff/noise and production gap:
  - Enforce output stripping on commit for training notebooks.
  - Extract reusable logic from repeated LLM/ML notebooks into `src/` modules, then notebooks become thin orchestration/examples.
- Add minimal CI validation for representative notebooks:
  - Smoke-run 1 notebook per cluster (RAG, LangGraph, ML, DS, TF) on clean env to catch dependency/data regressions early.