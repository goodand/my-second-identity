## Scope
- Central source analyzed: `LLM_013_Generation_Metrics_Me.ipynb`.
- Focused stack: heuristic checks, ROUGE/BLEU, string distance, embedding distance, LangSmith-based evaluation.
- Cross-checked supporting artifacts: `data/evaluation_dataset.csv`, `data/evaluation_results.json`, `data/ragas_evaluation_results.csv`, `data/synthetic_testset_revised.csv`.

## What is already implemented
- Heuristic evaluators in notebook:
  - String length and token length checks (`evaluate_string_length`, `evaluate_token_length`).
  - JSON validity check via `load_evaluator("json_validity")`.
  - Parallel evaluator chain pattern using `RunnableParallel`.
- ROUGE/BLEU:
  - ROUGE-1/2/L via `rouge_score` + `KiwiTokenizer`.
  - BLEU via `nltk.sentence_bleu` with smoothing and tokenizer support.
- String distance:
  - `load_evaluator("string_distance", distance="levenshtein")`.
  - LangSmith-integrated `LangChainStringEvaluator("string_distance")`.
- Embedding distance:
  - `load_evaluator("embedding_distance", distance_metric="cosine")`.
  - LangSmith-integrated `LangChainStringEvaluator("embedding_distance")` with `OpenAIEmbeddings("text-embedding-3-small")`.
- LangSmith:
  - Dataset creation and `evaluate(...)` execution patterns.
  - LLM-as-judge example using `create_llm_as_judge` (`openevals`).
- Existing offline data assets:
  - QA/reference datasets and prior RAGAS outputs in `data/`.

## What is missing for rigorous generation evaluation
- No productionized eval package/module; logic is notebook-only (`LLM_013_Generation_Metrics_Me.ipynb`).
- No fixed train/dev/test split policy or difficulty-stratified reporting (persona/query_style fields in `data/synthetic_testset_revised.csv` unused for slicing).
- No metric calibration:
  - No thresholds per metric, no acceptance gates, no pass/fail policy.
- No aggregate reporting standard:
  - Missing weighted composite score and confidence intervals/variance across runs.
- Weak reproducibility controls:
  - No pinned eval config schema, no seed policy, no snapshot versioning for dataset/model/prompt.
- No automated regression workflow:
  - No CI job to run eval and compare against baseline artifacts.
- Limited semantic/factual rigor:
  - Distances and n-gram overlap used, but citation-grounded faithfulness and factual error taxonomy are not integrated end-to-end.
- Online loop incomplete:
  - LangSmith is used, but no explicit production feedback rubric, alerting thresholds, or human review queue definition.
- Security/process gap:
  - API key appears hardcoded in notebook env setup (`LLM_013_Generation_Metrics_Me.ipynb`).

## Suggested metric protocol (offline + online)
- Offline (release gate):
  - Heuristic gate: format, length/token bounds, JSON validity (hard fail).
  - Lexical similarity: ROUGE-1/2/L + BLEU (diagnostic, not sole gate).
  - Surface/semantic similarity: normalized Levenshtein + embedding cosine distance.
  - LLM-as-judge: correctness + groundedness rubric with fixed prompt/version.
  - Slice reporting: by `query_style`, `query_length`, `persona_name`.
  - Gate rule example: fail if any hard-fail heuristic or if key quality metrics drop >X% vs baseline.
- Online (post-release monitoring):
  - LangSmith trace sampling + evaluator reruns on live traffic samples.
  - Human spot-check queue for low-confidence or high-disagreement cases.
  - Weekly drift dashboard: metric trend, failure taxonomy, slice drift.
  - Incident trigger: sustained degradation for N days or threshold breach in critical slice.

## Next 10 concrete tasks with file targets
1. Create a reusable eval config schema (`thresholds`, `weights`, `slices`, `models`) in `configs/eval/generation_eval.yaml`.
2. Build unified evaluator module (heuristic/ROUGE/BLEU/string/embedding/LangSmith adapters) in `src/eval/generation_metrics.py`.
3. Add dataset loader/normalizer for current CSV+JSON assets in `src/eval/datasets.py`.
4. Create offline eval runner CLI (`python -m ...`) in `src/eval/run_offline_eval.py`.
5. Add result aggregator with per-slice tables + composite score in `src/eval/reporting.py`.
6. Save baseline metrics snapshot in `artifacts/eval/baseline_generation_metrics.json`.
7. Add regression checker against baseline deltas in `src/eval/regression_guard.py`.
8. Externalize secrets and remove hardcoded key usage from notebook by introducing `.env.example` and using `.env` only; document in `docs/evaluation_setup.md`.
9. Add LangSmith online eval pipeline script (sample traces, rerun evaluators, export report) in `src/eval/run_online_eval.py`.
10. Add CI workflow to run offline eval + regression guard on PR in `.github/workflows/generation-eval.yml`.