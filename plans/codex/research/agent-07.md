## Scope
- Reviewed `data/` assets (CSV/TXT/JSON/PDF/DB/PKL), especially high-risk records in:
  - `data/membership.csv`
  - `data/sqlite-sakila.db`
  - `data/creditcard.csv`
  - `data/docling_output/tsla_analysis_ocr.pkl`
- Reviewed ELK infra/config in `docker-elk-main/`:
  - `docker-elk-main/docker-compose.yml`
  - `docker-elk-main/.env`
  - `docker-elk-main/elasticsearch/config/elasticsearch.yml`
  - `docker-elk-main/kibana/config/kibana.yml`
  - `docker-elk-main/logstash/pipeline/logstash.conf`
  - `docker-elk-main/extensions/*/{*-compose.yml,config/*.yml}`
- Reviewed dependency/env manifests:
  - `pyproject.toml`
  - `pyproject.docling.toml`
  - `requirements.txt`
  - `mcp-test/requirements.txt`
  - `.env`
- Caveat: Git-tracking status could not be verified because this directory is not a Git repo (`.git` missing).

## Data governance/privacy risks
- High: plaintext secrets in `.env` with live-looking API/service credentials (`OPENAI`, `GOOGLE`, `LANGSMITH`, `LANGFUSE`, `TAVILY`, `NEO4J`) in `.env`.
- High: secret replication in local history snapshots under `.history/.env_*`, increasing leak surface and rotation burden.
- High: hardcoded secrets in code/notebook artifacts:
  - `agent-made-by-gemini.py`
  - `LLM_013_Generation_Metrics_Me.ipynb`
  - `review-agent-2026.ipynb`
- High: likely personal data present in datasets without visible governance controls:
  - `data/membership.csv` includes income/age/gender/marital status/agent code.
  - `data/sqlite-sakila.db` contains customer names/emails/addresses (customer table).
- Medium: no visible data classification/retention/access policy artifacts near `data/` (no policy file, DLP rules, or masking pipeline references).
- Medium: unsafe serialized binary in data zone (`data/docling_output/tsla_analysis_ocr.pkl`), which is risky if deserialized from untrusted sources.

## Dependency and environment risks
- High: unpinned dependencies in `requirements.txt` and `mcp-test/requirements.txt` (`mcp[cli]`, `uvicorn`, `mcp[fastmcp]`) create non-reproducible builds and supply-chain drift.
- Medium: `pyproject.toml` and `pyproject.docling.toml` mostly use lower-bound ranges (`>=`) without upper bounds, allowing breaking updates.
- Medium: dependency model inconsistency across `requirements*.txt`, `pyproject*.toml`, and `uv.lock` risks environment drift and “works on my machine” failures.
- Medium: no `.gitignore` found at repo root; likely accidental inclusion risk for `.env`, local caches, notebooks with outputs, and history artifacts.

## Infra/ops risks
- Critical: Elasticsearch security disabled in `docker-elk-main/elasticsearch/config/elasticsearch.yml` (`xpack.security.enabled: false`).
- Critical: default weak credential remains in `docker-elk-main/.env` (`ELASTIC_PASSWORD='changeme'`), and several internal passwords are blank.
- High: pervasive plaintext HTTP/no TLS across stack:
  - `docker-elk-main/kibana/config/kibana.yml`
  - `docker-elk-main/logstash/pipeline/logstash.conf`
  - `docker-elk-main/extensions/*/config/*.yml`
  - `docker-elk-main/extensions/fleet/*compose.yml` (`FLEET_SERVER_INSECURE_HTTP`, `FLEET_INSECURE`)
- High: broad port exposure to host in `docker-elk-main/docker-compose.yml` (`9200`, `9300`, `5601`, `5044`, `50000`, `9600`) with weak/disabled auth.
- High: privileged host visibility from beats:
  - `docker-elk-main/extensions/filebeat/filebeat-compose.yml` mounts `/var/run/docker.sock` and container logs, runs as root.
  - `docker-elk-main/extensions/metricbeat/metricbeat-compose.yml` mounts `/`, `/proc`, `/sys/fs/cgroup`, docker socket; adds `SYS_PTRACE`; runs as root.
- Medium: Kibana encryption keys are commented out in `docker-elk-main/kibana/config/kibana.yml`, risking insecure session/saved-object crypto defaults.
- Medium: over-broad index privileges (`manage`, `manage_ilm`) in setup roles:
  - `docker-elk-main/setup/roles/*.json`

## Mitigation plan with priorities
- P0 (immediate, same day)
  1. Revoke and rotate all credentials exposed in `.env`, `.history/.env_*`, `agent-made-by-gemini.py`, and notebooks.
  2. Remove secrets from files; replace with env placeholders and a committed `.env.example` (no real values).
  3. Enable Elasticsearch auth/TLS in `docker-elk-main/elasticsearch/config/elasticsearch.yml`; enforce strong non-default passwords in `docker-elk-main/.env`.
  4. Disable insecure fleet flags and HTTP endpoints (`FLEET_SERVER_INSECURE_HTTP`, `FLEET_INSECURE`) in `docker-elk-main/extensions/fleet/*.yml`.

- P1 (this week)
  1. Restrict exposed ports in `docker-elk-main/docker-compose.yml` to localhost or internal networks only.
  2. Minimize host mounts/capabilities in beat compose files; remove docker socket and `/` bind unless strictly required.
  3. Enable Kibana encryption keys in `docker-elk-main/kibana/config/kibana.yml`.
  4. Tighten ELK role privileges in `docker-elk-main/setup/roles/*.json` to least privilege.
  5. Add root `.gitignore` to exclude `.env`, `.history/`, notebooks with outputs (or sanitize outputs), and local DB/cache artifacts.

- P2 (next sprint)
  1. Define and document data governance for `data/` (classification, retention, lawful basis, access controls, anonymization).
  2. De-identify or gate sensitive datasets (`data/membership.csv`, `data/sqlite-sakila.db`) behind controlled access.
  3. Ban unsafe pickle loading for external/untrusted files; migrate serialized artifacts to safer formats.
  4. Standardize dependency management on one source of truth (prefer `pyproject` + lock), and pin critical packages with tested ranges.