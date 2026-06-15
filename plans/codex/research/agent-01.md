## Scope
- Monorepo-style learning/workspace with multiple independent systems:
  - LangGraph QA prototype: `src/graph.py`, `langgraph.json`
  - Dependency analyzer package/CLI: `depsolve_ext/`
  - MCP weather demo servers: `mcp-test/weather_server.py`, `mcp-test/weather_server_sse.py`
  - ELK stack (vendored template): `docker-elk-main/`
- Large data + artifacts co-located with code: `data/`, `chroma_db/`, `local_chroma_db/`, `*.ipynb`, `*.db`, `*.zip_part`.

## Key directories/files
- `src/graph.py` (LangGraph state machine)
- `langgraph.json` (graph entry mapping to `src/graph.py:graph`)
- `pyproject.toml` (main Python env/deps)
- `pyproject.docling.toml` (second Python env/deps)
- `requirements.txt` (minimal MCP env)
- `depsolve_ext/__main__.py`, `depsolve_ext/cli.py`, `depsolve_ext/analyzer.py`, `depsolve_ext/graph.py`, `depsolve_ext/extensions.py`, `depsolve_ext/tests.py`
- `mcp-test/weather_server.py`, `mcp-test/weather_server_sse.py`, `mcp-test/requirements.txt`
- `docker-elk-main/docker-compose.yml`, `docker-elk-main/logstash/pipeline/logstash.conf`, `docker-elk-main/elasticsearch/config/elasticsearch.yml`, `docker-elk-main/kibana/config/kibana.yml`
- `data/`, `chroma_db/`, `local_chroma_db/`, `etf_database.db`
- `.env`, `.history/.env_*`

## System/data flow summary
1. LangGraph QA flow (`src/graph.py`)
- Input `user_query` -> `analyze_input` (LLM language detection) -> conditional route to `korean_rag_search` or `english_rag_search` -> `generate_response` (LLM).
- Uses vector DB handles (`db_korean`, `db_english`) but they are not defined in-file.

2. Dependency analysis flow (`depsolve_ext`)
- CLI entry `python -m depsolve_ext` -> `depsolve_ext/cli.py` commands -> `DependencyAnalyzer` (`depsolve_ext/analyzer.py`).
- Reads manifest/lockfiles, builds graph (`depsolve_ext/graph.py`), detects cycles/diamonds/phantoms/multi-version (`depsolve_ext/extensions.py`), outputs via reporters.

3. MCP weather flow (`mcp-test`)
- MCP client -> FastMCP tools/resources in `weather_server.py` or SSE endpoint in `weather_server_sse.py`.
- Returns static in-memory weather dict (no external persistence/API).

4. ELK flow (`docker-elk-main`)
- Log input -> Logstash -> Elasticsearch -> Kibana visualization.
- One-time setup service initializes users/roles from `docker-elk-main/.env`.

## Top 5 structural risks
1. Undefined runtime dependencies in core graph path
- `src/graph.py` references `db_korean`/`db_english` without initialization, causing runtime failure.

2. Repository boundary blur (code + huge artifacts + notebooks)
- `*.ipynb`, `data/`, `chroma_db/`, `local_chroma_db/`, `unsplash-25k-photos.zip_part` in root reduce maintainability and tooling performance.

3. Environment fragmentation
- Multiple dependency definitions: `pyproject.toml`, `pyproject.docling.toml`, `requirements.txt`, `mcp-test/requirements.txt` with no single source of truth.

4. Secret/config hygiene risk
- Root `.env` plus historical env snapshots in `.history/.env_*` increase leakage/misconfiguration risk.

5. Multiple independent systems without explicit architecture docs/ownership
- `src/`, `depsolve_ext/`, `mcp-test/`, `docker-elk-main/` coexist without root README/runbook, increasing onboarding and operational ambiguity.

## Immediate improvements (5)
1. Stabilize LangGraph entrypoint
- Define/initialize `db_korean` and `db_english` in `src/graph.py` (or inject via factory module, e.g., `src/rag_store.py`).

2. Introduce root architecture/runbook
- Add `README.md` at repo root with subsystem table, start commands, and boundaries for `src/`, `depsolve_ext/`, `mcp-test/`, `docker-elk-main/`.

3. Split code vs assets
- Move heavy datasets/artifacts to `artifacts/` or external storage; keep only required samples in `data/`; add `.gitignore` rules for generated DB/index outputs.

4. Consolidate dependency management
- Choose one primary env strategy (prefer `pyproject.toml` + `uv.lock`), and make `mcp-test`/docling either workspace extras or isolated subprojects with clear ownership.

5. Harden config/security handling
- Add `.env.example`; remove/ignore `.history/.env_*`; document required vars in one place (`README.md`), and avoid storing historical secret-bearing files.