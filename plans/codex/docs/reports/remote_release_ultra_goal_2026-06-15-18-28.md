# Remote Release Ultra Goal

- created_at: `2026-06-15-18-28`
- scope_owner: `codex`
- machine_contract: `plans/codex/docs/references/remote_release_scope_contract_2026-06-15-18-28.json`
- validator: `scripts/release/validate_remote_release_gate.py`

## Ultra Goal

GitHub 원격 저장소의 `main` 브랜치를 재현 가능한 RAG 실험/개발 기준점으로 만든다.

이 goal의 핵심은 새 실험을 더 실행하는 것이 아니라, 이미 정리한 코드, 설정, 문서, 산출물 구조가 원격 저장소에 안전하게 올라갔는지 코드로 판정하는 것이다.

## Goals

1. RAG 코드 변경이 원격 `main`에 반영되어야 한다.
2. Chroma persistence 경로가 설정 파일 기본값과 환경 변수 override를 모두 지원해야 한다.
3. HyDE/CandidateBundle provenance 계약이 테스트와 코드에 반영되어야 한다.
4. `plans/**` 문서와 산출물이 owner directory 기준으로 정리되어야 한다.
5. runtime, cache, log, local DB, secret-like 파일이 tracked scope에 들어오지 않아야 한다.
6. moved planning documents가 stale relative link를 남기지 않아야 한다.
7. 위 조건은 사람이 읽는 문서가 아니라 실행 가능한 validator로 반복 검증할 수 있어야 한다.

## Non-Goals

1. 새 Docling 실험을 실행하지 않는다.
2. answerable45/65Q 평가를 새로 돌리지 않는다.
3. Obsidian vault 구조 확장을 포함하지 않는다.
4. 로컬 dirty worktree 전체를 정리하는 작업을 포함하지 않는다.
5. generated experiment outputs, cache, logs, Chroma DB, `.env`, `.mcp.json`을 원격 저장소에 올리지 않는다.
6. 기존 RAG metric 정의를 변경하지 않는다.
7. validator가 자동으로 무한 루프를 돌며 파일을 수정하지 않는다.

## Included Scope

1. `src/rag/bootstrap.py`
2. `src/rag/graph.py`
3. `src/rag/candidates.py`
4. `configs/rag.yaml`
5. `.gitignore`
6. `uv.lock`
7. `tests/rag/test_bootstrap_config.py`
8. `tests/rag/test_candidate_bundle.py`
9. `tests/rag/test_hyde_variant.py`
10. `plans/claude/**`
11. `plans/gemini/**`
12. `plans/codex/docs/**`
13. `plans/codex/research/**`
14. `plans/codex/image-arch/**`
15. release gate contract and validator files added by this task

## Excluded Scope

1. `.env`
2. `.mcp.json`
3. `logs/**`
4. `tmp/**`
5. `*.log`
6. `*.pid`
7. `.pytest_cache/**`
8. `**/__pycache__/**`
9. `**/*.pyc`
10. `local_chroma_db*/**`
11. `*chroma_db*/**`
12. `plans/codex/.git/**`
13. `plans/codex/.pytest_cache/**`
14. `plans/codex/.tmp/**`
15. `plans/codex/test_result/**`
16. `plans/claude/*.log`
17. `plans/claude/*.json`

## Code-Verifiable Gates

The machine-readable contract defines these gates:

1. `GATE-CONTRACT-SHAPE`: contract has goals, non-goals, included scope, excluded scope, and gates.
2. `GATE-REQUIRED-PATHS`: required code, config, tests, and reorganized docs exist and are tracked by git.
3. `GATE-FORBIDDEN-TRACKED`: excluded runtime/generated/local paths are not tracked by git.
4. `GATE-REQUIRED-HISTORY`: expected release commit subjects are present in local history.
5. `GATE-FILE-CONTAINS`: key files and tests contain the expected contract markers.
6. `GATE-NO-STALE-PLAN-LINKS`: moved planning documents do not contain known stale links.

## Execution Rule

Run the validator as a one-shot gate:

```bash
python scripts/release/validate_remote_release_gate.py \
  --contract plans/codex/docs/references/remote_release_scope_contract_2026-06-15-18-28.json \
  --repo .
```

The validator exits with `0` only when all gates pass. A runner can repeat this command until pass, but the validator itself must stay deterministic and non-mutating.
