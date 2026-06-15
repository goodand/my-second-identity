# plans/** Diff Classification

- created_at: `2026-06-15-15-51`
- scope: `plans/**` deletion/move audit for PR sequencing
- decision_rule: `재생성 가능한 것 > 재현 가능한 것 > 자연어로 표현 가능한 것`
- lifecycle_rule_source: `artifact-lifecycle-manager`
- user_decision:
  - `plans/image-arch/* -> plans/codex/image-arch/*`: `A 승인`

## Decision Classes

| class | meaning | default action |
|---|---|---|
| `approved_move_exact` | hash-identical move and user approved | keep new path, allow old path deletion |
| `move_exact` | hash-identical move | keep new path, allow old path deletion |
| `move_updated` | same artifact family, content/path references updated | keep new path, run link audit before final stage |
| `move_supersede` | new artifact materially expands old artifact | keep successor, do not restore old path |
| `restore_or_move_required` | deleted natural-language artifact has no equivalent successor | restore old content or move it to declared new canonical path |
| `exclude_generated` | generated/runtime/cache output | do not stage for PR |

## Deleted Tracked Files

| old path | candidate successor | evidence | class | action |
|---|---|---|---|---|
| `plans/CLAUDE_REVIEW_REQUEST.md` | `plans/claude/CLAUDE_REVIEW_REQUEST.md` | SHA differs, direct read shows same review-request role with moved path references. Some references still point to missing or old codex paths. | `move_updated` | Keep successor; fix links before stage. |
| `plans/PLAN.md` | `plans/gemini/PLAN.md` | SHA differs, direct read shows same RAG upgrade plan role with document-map updates. Links still reference `../codex/RAG_URL_KNOWLEDGE_BASE.md` and `../codex/MASTER_SUMMARY.md`, which no longer match current successors. | `move_updated` | Keep successor; fix links before stage. |
| `plans/IMAGE_STRUCTURE_GRAPHS.md` | `plans/gemini/IMAGE_STRUCTURE_GRAPHS.md` | SHA differs, direct read shows same diagram explanation role with source path moved to `plans/codex/image-arch/index.txt`. KB links still use old `../codex/RAG_URL_KNOWLEDGE_BASE.md`. | `move_updated` | Keep successor; fix links before stage. |
| `plans/IMAGE_URL_MATCHES.md` | `plans/gemini/IMAGE_URL_MATCHES.md` | SHA differs, direct read shows same image URL matching role. Sources still mention old `plans/codex/RAG_URL_KNOWLEDGE_BASE.md`. | `move_updated` | Keep successor; fix links before stage. |
| `plans/RAG_URL_KNOWLEDGE_BASE.md` | `plans/codex/docs/knowledge/RAG_URL_KNOWLEDGE_BASE.md` | SHA differs; successor expands the KB from the old set to a larger v2-style paper/reference index. | `move_supersede` | Keep successor; fix relative links from its deeper directory. |
| `plans/_rag_notebooks.txt` | `plans/codex/_rag_notebooks.txt` | SHA differs; successor keeps notebook inventory role but rewrites entries as `file://` markdown links. | `move_updated` | Keep successor; review absolute `file://` policy before stage. |
| `plans/notebooks.md` | `plans/codex/docs/notes/notebooks.md` | SHA identical: `adac8f81371918a807b7e49968232f51024e5eabe75fb47e6886dc39b1a741a7`. | `move_exact` | Keep successor; old deletion is safe. |
| `plans/codex/MASTER_SUMMARY.md` | `plans/codex/docs/notes/MASTER_SUMMARY.md` | SHA differs, direct read shows same master-summary role with path updates. It references missing `plans/codex/research/agent-*.md` and wrong relative KB/Gemini paths. | `move_updated` | Keep successor; fix links and restore/move agent reports before stage. |
| `plans/codex/agent-01.md` | none confirmed | Old file is a 67-line architecture report. `plans/agents/result-agent-01.md` is a 5-line URL/source list; `plans/agents/pseudocode/agent-01.md` is also not equivalent. `plans/codex/research/agent-01.md` does not exist. | `restore_or_move_required` | Do not accept deletion. Restore old content or move to `plans/codex/research/agent-01.md`. |
| `plans/codex/agent-02.md` | none confirmed | Old file is a 49-line runtime/security report. Existing result/pseudocode files are short non-equivalent summaries. | `restore_or_move_required` | Do not accept deletion. Restore old content or move to `plans/codex/research/agent-02.md`. |
| `plans/codex/agent-03.md` | none confirmed | Old file is a 40-line deep diagnostic report. Existing result/pseudocode files are short non-equivalent summaries. | `restore_or_move_required` | Do not accept deletion. Restore old content or move to `plans/codex/research/agent-03.md`. |
| `plans/codex/agent-04.md` | none confirmed | Old file is a 48-line MCP readiness report. Existing result/pseudocode files are short non-equivalent summaries. | `restore_or_move_required` | Do not accept deletion. Restore old content or move to `plans/codex/research/agent-04.md`. |
| `plans/codex/agent-05.md` | none confirmed | Old file is a 78-line notebook/reproducibility report. Existing result/pseudocode files are short non-equivalent summaries. | `restore_or_move_required` | Do not accept deletion. Restore old content or move to `plans/codex/research/agent-05.md`. |
| `plans/codex/agent-06.md` | none confirmed | Old file is a 67-line generation-metrics/eval report. Existing result/pseudocode files are short non-equivalent summaries. | `restore_or_move_required` | Do not accept deletion. Restore old content or move to `plans/codex/research/agent-06.md`. |
| `plans/codex/agent-07.md` | none confirmed | Old file is a 74-line data/infra/environment-risk report. Existing result/pseudocode files are short non-equivalent summaries. | `restore_or_move_required` | Do not accept deletion. Restore old content or move to `plans/codex/research/agent-07.md`. |
| `plans/codex/agent-08.md` | none confirmed | Old file is a 91-line repo-wide risk and 30/60/90 roadmap report. Existing result/pseudocode files are short non-equivalent summaries. | `restore_or_move_required` | Do not accept deletion. Restore old content or move to `plans/codex/research/agent-08.md`. |
| `plans/image-arch/01.png` ... `plans/image-arch/08.png` | `plans/codex/image-arch/01.png` ... `plans/codex/image-arch/08.png` | SHA identical for all 8 images; user visually approved move as `A 승인`. | `approved_move_exact` | Keep successor images; old deletion is safe. |
| `plans/image-arch/index.txt` | `plans/codex/image-arch/index.txt` | SHA identical. | `approved_move_exact` | Keep successor; old deletion is safe. |
| `plans/image-arch/targets.txt` | `plans/codex/image-arch/targets.txt` | SHA identical. | `approved_move_exact` | Keep successor; old deletion is safe. |

## Untracked Generated/Runtime Scope

The following paths are not part of the document move decision and should stay out of PR #5 unless a later task explicitly promotes them:

| path pattern | reason | class | action |
|---|---|---|---|
| `plans/codex/.git/**` | nested git metadata/runtime artifact | `exclude_generated` | Do not stage. |
| `plans/codex/.pytest_cache/**` | test cache | `exclude_generated` | Do not stage. |
| `plans/codex/**/__pycache__/**` | Python bytecode cache | `exclude_generated` | Do not stage. |
| `plans/codex/.tmp/**` | temporary execution output | `exclude_generated` | Do not stage. |
| `plans/codex/test_result/**` | reproducible experiment outputs and logs; may need separate artifact policy | `exclude_generated` | Do not stage in cleanup PR by default. |
| `plans/claude/*.log` | runtime logs | `exclude_generated` | Do not stage unless promoted into a report. |
| `plans/claude/*.json` | measurement output artifacts | `exclude_generated` | Do not stage unless explicitly selected as evidence. |

## Required Fixes Before PR #5 Stage

1. Restore or move `plans/codex/agent-01.md` ... `plans/codex/agent-08.md` into the path family referenced by successors, preferably `plans/codex/research/agent-01.md` ... `plans/codex/research/agent-08.md`.
2. Fix moved-document links that still point to old `plans/codex/RAG_URL_KNOWLEDGE_BASE.md`, old `plans/codex/MASTER_SUMMARY.md`, or missing `plans/codex/research/agent-*.md`.
3. Keep exact image moves as approved by user.
4. Do not stage generated/runtime paths from `plans/codex/.git`, `.pytest_cache`, `__pycache__`, `.tmp`, or `test_result` in the cleanup PR.

## Follow-up Fix Status

- checked_at: `2026-06-15-16-44`
- `plans/codex/research/agent-01.md` ... `plans/codex/research/agent-08.md`: restored from original tracked blobs; SHA matches original `plans/codex/agent-01.md` ... `plans/codex/agent-08.md`.
- `plans/claude/CLAUDE_REVIEW_REQUEST.md`: updated literal successor paths for `MASTER_SUMMARY.md` and `RAG_URL_KNOWLEDGE_BASE.md`.
- `plans/gemini/PLAN.md`: updated KB/Master links to `../codex/docs/knowledge/RAG_URL_KNOWLEDGE_BASE.md` and `../codex/docs/notes/MASTER_SUMMARY.md`.
- `plans/gemini/IMAGE_STRUCTURE_GRAPHS.md`: updated KB links to `../codex/docs/knowledge/RAG_URL_KNOWLEDGE_BASE.md`.
- `plans/gemini/IMAGE_URL_MATCHES.md`: updated KB link and source path literals to `plans/codex/docs/knowledge/RAG_URL_KNOWLEDGE_BASE.md`.
- `plans/codex/docs/knowledge/RAG_URL_KNOWLEDGE_BASE.md`: updated Gemini links from old depth to `../../../gemini/...`.
- `plans/codex/docs/notes/MASTER_SUMMARY.md`: updated Gemini, KB, and research-agent links from old depth to current canonical locations.
- link-pattern check: no remaining `plans/codex/RAG_URL_KNOWLEDGE_BASE.md`, `plans/codex/MASTER_SUMMARY.md`, `](../codex/RAG_URL_KNOWLEDGE_BASE.md)`, `](../codex/MASTER_SUMMARY.md)`, `](../gemini/...)`, `](RAG_URL_KNOWLEDGE_BASE.md)`, or `](research/agent-*.md)` in the reviewed successor docs.
