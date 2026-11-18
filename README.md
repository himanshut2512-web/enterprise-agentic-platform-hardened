# Aegis Grounded Agent — Enterprise Operations Platform

This repository implements the end-to-end architecture specified in `design.md` and `WORKFLOW_PLANNER.md`.

## Run locally

```bash
make install
make api
make ui
```

Open the API docs at `http://localhost:8000/docs` and Streamlit at `http://localhost:8501`.

## Components

- `app/main.py`: FastAPI application and REST API
- `app/core/agent.py`: bounded routing and execution agent
- `app/core/rag.py`: BM25 + dense similarity + RRF + rerank implementation
- `app/core/harness.py`: validation, repair, RBAC and circuit breaker
- `app/plugins/security.py`: PII and injection controls
- `app/core/state.py`: tenant-isolated cache and audit state
- `app/mcp_servers/`: MCP-style JSON-RPC service boundaries
- `ui/app.py`: six-tab Streamlit workbench
- `tests/test_application.py`: core behavior tests
- `eval/kpi_validator.py`: 36-KPI release gate matrix

## Core API

`POST /api/v1/agent/query`

```json
{
  "tenant_id": "tenant_acme",
  "user_id": "user_1001",
  "session_id": "00000000-0000-4000-8000-000000000001",
  "query": "What is the credential rotation policy?"
}
```

## Safety behavior

- PII is redacted before model-facing processing.
- Prompt-injection markers produce a fail-closed refusal.
- Tier-3 mutations create a pending approval instead of mutating state.
- Low-confidence retrieval returns an abstention response.
- Every answer includes audit trace and evidence when grounded.

## Validation

```bash
pytest -q
python eval/kpi_validator.py
```
