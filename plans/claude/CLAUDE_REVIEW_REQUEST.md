# Review Request: RAG Upgrade Workspace Progress

Context
- Workspace: `/Users/jaehyuntak/Desktop/gangnam-1st`
- Goal: Build a new workspace for RAG performance uplift (evaluation + retrieval/generation improvement + operationalization).
- This request asks for rigorous review of: factual validity, methodological soundness, and alignment to goal.

## What has been done

1) Multi-agent repo analysis (8 agents)
- Ran 8 Codex agents in parallel and produced reports in:
  - `plans/codex/research/agent-01.md` ... `plans/codex/research/agent-08.md`
- Consolidated summary:
  - `plans/codex/docs/notes/MASTER_SUMMARY.md`

2) RAG-upgrade planning docs (consolidated, minimal set)
- Canonical plan + reading manual + 8-agent operation protocol:
  - `plans/gemini/PLAN.md`
- Canonical URL knowledge base for RAG references:
  - `plans/codex/docs/knowledge/RAG_URL_KNOWLEDGE_BASE.md`

3) URL mining and curation
- Scanned RAG-related notebooks and collected URLs.
- Added per-paper metadata under `Paper-like URLs`:
  - `key_idea`
  - `execution_conditions`
  - `pseudocode_3lines`
- Added `pseudocode_3lines` also under `Other RAG References URLs`.

4) Image URL matching and architecture extraction
- Matched image URLs in workspace against RAG URL KB:
  - `plans/gemini/IMAGE_URL_MATCHES.md`
- Downloaded 8 target images and extracted structure representations:
  - index: `plans/codex/image-arch/index.txt`
  - local files: `plans/codex/image-arch/01.png` ... `08.png`
  - graph output: `plans/gemini/IMAGE_STRUCTURE_GRAPHS.md`
- For each image, produced:
  - Mermaid flow
  - Adjacency list
- Note: `02` image URL redirected to non-image HTML; structure reconstructed from documented concept.

5) Claude runtime issue prevention skill
- Root cause diagnosed: Node v25 incompatibility (SlowBuffer removal path), verified by runtime behavior.
- Recovery tested: Node 22 LTS via nvm -> Claude CLI 정상.
- Created reusable skill:
  - `skills/claude/SKILL.md`
  - `skills/claude/scripts/repair_claude_node.sh`
  - `skills/claude/agents/openai.yaml`

## Request for your review
Please evaluate with strict engineering standards.

A. Validity / Correctness
1. Are the derived `key_idea` and `execution_conditions` for each paper plausible and technically accurate?
2. Are `pseudocode_3lines` faithful abstractions (not misleading over-simplifications)?
3. Are image-to-graph conversions in `IMAGE_STRUCTURE_GRAPHS.md` reasonable given the source figures?

B. Alignment to goal
1. Does current artifact set support the stated goal (RAG performance uplift in a new workspace)?
2. Are there critical missing artifacts to transition from research notes to executable roadmap?

C. Risk / Gaps
1. Identify top 5 risks (severity-ordered) that could make this plan fail.
2. Flag any hallucination-prone or weakly grounded sections in current docs.

D. Actionable next steps
1. Provide a concrete next 2-week plan (day-level or milestone-level).
2. Propose minimal doc/version hygiene to avoid drift while preserving speed.

## Response format (required)
1) Critical Findings (<=5, severity ordered)
2) Medium Findings
3) Confirmed Strengths
4) 2-Week Execution Plan
5) Final Verdict:
- factual_validity: high|medium|low
- goal_alignment: high|medium|low
- confidence: high|medium|low
