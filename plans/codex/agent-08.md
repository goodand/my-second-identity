## Scope
- Repository-wide static scan across code, config, docs, data, and infra assets, including `src/`, `depsolve_ext/`, `mcp-test/`, `docker-elk-main/`, `plans/codex/`, `data/`, and top-level project files.
- Baseline composition observed: 66 notebooks (`*.ipynb`), 19 Python files (depth<=2), large binary/data footprint (e.g., `unsplash-25k-photos.zip_part`, `data/`, `elk/`), and no root Git metadata (root lacks `.git`, while `mcp-test/.git` exists).

## Top 10 repo-wide risks (ordered by severity)
1. **Credential exposure in source and artifacts**  
   Hardcoded keys/tokens appear in executable code and notebooks: `agent-made-by-gemini.py:12`, `agent-made-by-gemini.py:15`, `LLM_013_Generation_Metrics_Me.ipynb:57`, `review-agent-2026.ipynb:60`; additional leakage appears in logs: `plans/codex/agent-07.run.log:110`, `plans/codex/agent-02.run.log:86`.

2. **Secrets management is structurally unsafe**  
   Root `.env` contains many live credential variables (OpenAI/Langfuse/LangSmith/Tavily/Neo4j) and is directly referenced by runtime config: `.env`, `langgraph.json:7`.

3. **No root-level version control governance**  
   Root is not a Git repo (no `.git`), but a nested repo exists in `mcp-test/.git`; this blocks reliable change audit and release discipline across the full workspace.

4. **Operationally insecure infra defaults are present**  
   ELK stack exposes multiple ports and documents insecure default credentials/bootstrap posture: `docker-elk-main/docker-compose.yml:69`, `docker-elk-main/docker-compose.yml:94`, `docker-elk-main/docker-compose.yml:115`, `docker-elk-main/docker-compose.yml:81`, `docker-elk-main/README.md:168`, `docker-elk-main/README.md:111`.

5. **Primary runtime graph is not self-contained/executable as written**  
   Undefined dependencies are used in critical path (`db_korean`, `db_english`) with no initialization/validation: `src/graph.py:48`, `src/graph.py:61`; same graph is bound for both agents: `langgraph.json:4`, `langgraph.json:5`.

6. **Dependency/source-of-truth fragmentation**  
   Conflicting dependency declarations across files: `pyproject.toml`, `pyproject.docling.toml`, `requirements.txt`; additionally `pyproject.toml:5` expects `README.md` that is absent at root.

7. **Silent exception handling masks failures**  
   Broad catch-and-ignore patterns reduce diagnosability and can hide incorrect analysis output: `depsolve_ext/analyzer.py:157`, `depsolve_ext/analyzer.py:188`, `depsolve_ext/analyzer.py:238`, `depsolve_ext/extensions.py:115`, `depsolve_ext/extensions.py:688`, `depsolve_ext/cli.py:43`.

8. **Data governance and potential PII/compliance exposure**  
   Repository contains legal/personal/financial datasets and databases in working tree without visible governance controls: `data/personal_info_law.pdf`, `data/creditcard.csv`, `data/membership.csv`, `data/sqlite-sakila.db`, `etf_database.db`, `elk/TL_span_extraction.json`.

9. **Repository bloat harms developer throughput and CI feasibility**  
   Very large artifacts are stored directly in workspace: `unsplash-25k-photos.zip_part` (~1.5GB), `data/`, `elk/`, `local_chroma_db/`, `chroma_db/`.

10. **Testing and automation are uneven across components**  
   `depsolve_ext/tests.py` exists and passes, but equivalent tests/CI are absent for `src/` and `mcp-test/`; no root CI config found (only vendor subtree has one): `depsolve_ext/tests.py`, `src/graph.py`, `mcp-test/weather_server.py`, `docker-elk-main/.github/`.

## Top 10 opportunities
1. **Immediate secret remediation program**  
   Rotate exposed credentials, purge sensitive history/artifacts, and move to env-only secrets; target files: `agent-made-by-gemini.py`, `.env`, `plans/codex/*.run.log`, `LLM_013_Generation_Metrics_Me.ipynb`, `review-agent-2026.ipynb`.

2. **Unify repository governance at root**  
   Initialize root Git, absorb or deliberately separate `mcp-test/.git`, and define branching/release policy.

3. **Harden runtime entrypoints with explicit config validation**  
   Add startup checks for required services and keys in `src/graph.py` and align with `langgraph.json`.

4. **Promote `depsolve_ext` as the production core**  
   It already has architecture + tests (`depsolve_ext/*.py`, `depsolve_ext/tests.py`); package and publish internal tooling from this stable nucleus.

5. **Consolidate dependency strategy**  
   Pick one canonical dependency model (`pyproject.toml` + lock) and align `requirements.txt`/`pyproject.docling.toml`.

6. **Create top-level project contract and onboarding docs**  
   Add root `README.md` to satisfy `pyproject.toml:5` and document project boundaries (training notebooks vs shippable modules).

7. **Segment data and artifacts lifecycle**  
   Separate raw/sensitive data from code, add retention/cleanup policy for `data/`, `elk/`, `local_chroma_db/`, `chroma_db/`.

8. **Introduce CI quality gates for code paths that matter**  
   Start with lint/test/security scan on `depsolve_ext/`, `src/`, `mcp-test/`; include secret scanning and notebook output checks.

9. **Standardize MCP service packaging and deployment**  
   Convert demo servers (`mcp-test/weather_server.py`, `mcp-test/weather_server_sse.py`) into validated, testable service modules.

10. **Right-size repository footprint**  
   Move large binary assets to external storage/LFS and keep only references/metadata in repo (`unsplash-25k-photos.zip_part`, large image/data blobs).

## 30/60/90 day action roadmap
- **Day 0-30**
  1. Contain security exposure: rotate keys, remove hardcoded credentials, and scrub sensitive notebook/log outputs (`agent-made-by-gemini.py`, `plans/codex/`, `LLM_013_Generation_Metrics_Me.ipynb`, `review-agent-2026.ipynb`, `.env`).
  2. Establish repo control: create root Git governance and resolve nested repo strategy (`mcp-test/.git`).
  3. Add root documentation and project boundaries (`README.md`, align with `pyproject.toml:5`).
  4. Add fail-fast config checks and dependency injection points in runtime graph (`src/graph.py`, `langgraph.json`).

- **Day 31-60**
  1. Dependency unification and reproducible environments (`pyproject.toml`, `pyproject.docling.toml`, `requirements.txt`, `uv.lock`).
  2. CI pipeline for lint/test/security + secret scanning across production paths (`depsolve_ext/`, `src/`, `mcp-test/`).
  3. Refactor broad exception handling into typed failures and surfaced diagnostics (`depsolve_ext/analyzer.py`, `depsolve_ext/extensions.py`, `depsolve_ext/cli.py`).

- **Day 61-90**
  1. Productize `depsolve_ext` as internal tool/package with release versioning and changelog (`depsolve_ext/__init__.py`, `depsolve_ext/README.md`).
  2. Data governance implementation: data catalog, sensitivity labels, storage policy, and artifact migration off repo (`data/`, `elk/`, `local_chroma_db/`, `chroma_db/`).
  3. Operational hardening for infra demos: secure profiles and defaults for ELK + MCP deployment patterns (`docker-elk-main/docker-compose.yml`, `mcp-test/weather_server_sse.py`).

## Questions to resolve before implementation
1. Is this repository intended to be **production software**, **training material**, or both? (Impacts strictness for `src/` vs notebook areas.)
2. Which files are in official scope for security/compliance hardening: only code paths (`src/`, `depsolve_ext/`, `mcp-test/`) or all artifacts (`plans/`, notebooks, datasets)?
3. Should `mcp-test/` remain an independent repo, or be merged under root governance?
4. What is the canonical dependency manager going forward (`uv`/`pyproject` vs `requirements.txt`)?
5. What data classes are permitted in-repo, and which must be externalized? (`data/`, `elk/`, `*.db`, vector stores)
6. Do you want `docker-elk-main/` treated as vendored reference-only or operational infrastructure to harden and run?
7. Should notebooks be executable deliverables or converted into tested modules over time?
8. What is the target deployment/runtime for `src/graph.py` (local-only, LangGraph API, cloud service), and what SLA/reliability level is required?