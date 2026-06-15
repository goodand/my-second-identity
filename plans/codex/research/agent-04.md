## Scope
- Reviewed MCP server code:
  - `mcp-test/weather_server.py:4`
  - `mcp-test/weather_server_sse.py:5`
  - `mcp-test/requirements.txt:1`
- Reviewed LangGraph config/integration surface:
  - `langgraph.json:2`
  - `src/graph.py:1`
- Reviewed MCP notebook artifacts:
  - `LLM_017_MCP.ipynb:342`
  - `LLM_017_MCP.ipynb:447`
  - `LLM_017_MCP.ipynb:529`

## Current MCP/server behavior summary
- `mcp-test/weather_server.py` is a local/demo FastMCP server (`mcp.run()` default stdio) with:
  - Tools: `get_weather`, `get_temperature` (`mcp-test/weather_server.py:16`, `mcp-test/weather_server.py:23`)
  - Resource: `weather://{city}` (`mcp-test/weather_server.py:30`)
  - Prompt: `weather_report` (`mcp-test/weather_server.py:38`)
- `mcp-test/weather_server_sse.py` is SSE/HTTP-facing (`host="0.0.0.0"`, `port=$PORT`, `mcp.run(transport="sse")`) with only one tool (`get_weather`) (`mcp-test/weather_server_sse.py:10`, `mcp-test/weather_server_sse.py:21`, `mcp-test/weather_server_sse.py:29`).
- `langgraph.json` defines two graph names pointing to the same object and has no MCP server/client wiring (`langgraph.json:4`, `langgraph.json:5`).
- `src/graph.py` has no MCP usage/imports; current LangGraph flow is independent from MCP.
- `LLM_017_MCP.ipynb` is tutorial-style and instructs writing `weather_server.py`/`weather_server_sse.py` plus inspector/cloud steps, but this is not integrated into `langgraph.json` runtime.

## Operational/security risks
- No authn/authz on SSE server exposed on `0.0.0.0` (`mcp-test/weather_server_sse.py:10`).
- No input validation/rate limiting/request size limits on tool inputs.
- No transport hardening controls in code (TLS termination, origin restrictions, token checks).
- Minimal error handling; startup/runtime failures are not trapped or normalized.
- Dependency/config drift risk:
  - Root `requirements.txt` uses `mcp[cli]` while `mcp-test/requirements.txt` uses `mcp[fastmcp]`.
- Integration drift risk: notebook-generated file paths (`weather_server.py`) differ from repo structure (`mcp-test/weather_server.py`), increasing operator confusion.

## Missing observability/logging controls
- No structured logging for tool calls, latency, errors, or client identity.
- No metrics export (request count, failure rate, tool-level latency, SSE connection stats).
- No tracing/correlation IDs between LangGraph flows and MCP calls.
- No health/readiness endpoints or startup self-checks.
- No audit trail for resource/prompt/tool access.

## Action checklist for production readiness
- [ ] Add auth in front of SSE endpoint (API gateway token/mTLS) and reject unauthenticated clients.
- [ ] Add strict input schemas/validation and bounded payloads for all tools/resources.
- [ ] Add structured JSON logging (request ID, tool, status, latency, error class) in `mcp-test/weather_server*.py`.
- [ ] Add metrics/tracing (OpenTelemetry or equivalent) and alertable SLOs.
- [ ] Add health/readiness checks and graceful shutdown handling.
- [ ] Unify dependency strategy (`mcp[fastmcp]` vs `mcp[cli]`) and pin versions.
- [ ] Add tests for stdio + SSE behavior (tool/resource/prompt registration and error paths).
- [ ] If MCP is intended in LangGraph runtime, explicitly integrate MCP client code and wire it via graph config; currently `langgraph.json` has no MCP integration.
- [ ] Align notebook instructions with actual repo paths (`mcp-test/...`) to remove operational drift.