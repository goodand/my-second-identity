## Scope
Reviewed Python source quality and runtime risks in:
- `src/graph.py`
- `agent-made-by-gemini.py` (also the only root-level Python script)

## Findings (bug/risk oriented)
1. **P0 Security leak: hardcoded secrets in source**  
`agent-made-by-gemini.py:12`, `agent-made-by-gemini.py:15` embed OpenAI/LangSmith API keys directly. This is immediate credential-compromise risk.

2. **P0 Runtime crash risk: undefined dependencies used**  
`src/graph.py:48` and `src/graph.py:61` reference `db_korean` / `db_english` without definition/import, causing `NameError` at runtime when those nodes execute.

3. **P1 Import-time side effects make module fragile**  
`src/graph.py:8`, `src/graph.py:11`, `src/graph.py:115-137` initialize env/model/graph at import time; failures in env/config/network can break import before any caller handles errors.

4. **P1 Import-time env mutation and telemetry enablement**  
`agent-made-by-gemini.py:25-35` mutates process env and force-enables tracing on import, causing hidden side effects and accidental data egress.

5. **P1 Brittle routing logic due to free-form LLM parsing**  
`src/graph.py:37-39` assumes exact `"true"` text. Outputs like `"True."`, `"예"` or explanation text route incorrectly, causing wrong retrieval path.

6. **P2 Optional dependency can break execution**  
`src/graph.py:112` imports `IPython.display` though unused. In non-notebook environments without IPython, this can fail unnecessarily.

7. **P2 Type contract mismatch hides defects**  
Node functions in `src/graph.py` annotate returning full `EelectricCarState` but actually return partial dicts (e.g. `src/graph.py:41`, `src/graph.py:54`, `src/graph.py:67`, `src/graph.py:97`). This weakens static validation and can mask missing-key bugs.

## Reliability and error-handling gaps
- No `try/except` around model calls (`src/graph.py:37`, `src/graph.py:88`, `agent-made-by-gemini.py:97`), so transient API/network/auth failures bubble up unhandled.
- No fallback when retrieval returns empty/None docs (`src/graph.py:48-52`, `src/graph.py:61-65`), so response quality degrades silently.
- No startup validation for required config (`OPENAI_API_KEY`, vector DB availability, LangSmith key validity).
- `agent-made-by-gemini.py:18-23` fallback prompt is effectively dead because `api_key` is prefilled with a real key string, so missing-key flow is not reliable.
- No timeout/retry/backoff controls on external API calls.
- `main()` has no user-facing failure mode; exceptions will terminate process with stack trace only.

## Testability gaps
- Heavy global state and import-time initialization in both files prevents isolated unit tests.
- No dependency injection for LLM/vector stores (`src/graph.py`, `agent-made-by-gemini.py`), making mocking difficult.
- No deterministic seams for language classification and routing decisions.
- No tests for edge cases: undefined DBs, empty search results, malformed LLM outputs, auth failures.
- No contract tests for tool behavior and stream event shape in `agent-made-by-gemini.py`.

## Top 7 fixes with priorities
1. **P0** Remove hardcoded credentials from `agent-made-by-gemini.py`; load from env/secret manager only, rotate exposed keys immediately.  
2. **P0** Define and inject `db_korean`/`db_english` explicitly in `src/graph.py` (constructor/factory pattern), with startup validation.  
3. **P1** Move all side-effectful initialization behind `main()` or explicit builder functions in both files to make imports safe.  
4. **P1** Add robust error handling around LLM and retrieval calls (timeout, retries, structured exceptions, user-safe fallback responses).  
5. **P1** Replace free-form `"True"/"False"` parsing in `src/graph.py` with deterministic classifier output (JSON schema / enum / regex-normalized parser).  
6. **P2** Remove or guard `IPython.display` import in `src/graph.py`; keep notebook-only code optional.  
7. **P2** Refactor for testability: dependency injection for model/stores/tools and add focused tests for routing, empty results, and API failure paths.