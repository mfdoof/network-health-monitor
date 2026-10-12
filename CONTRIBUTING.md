# Contributing

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r api/requirements-dev.txt
cd client && npm ci
```

## Before opening a PR

From the repo root, with the venv active:

```bash
ruff check
pytest
cd client && npm run lint && npm run build
```

Tests mock DNS and HTTP and must not make real network calls.

## Rules

- One change per PR, with a short description of what and why.
- Keep the security defaults: target checks by resolved IP, `ALLOW_PRIVATE_TARGETS=false`, `LLM_REDACT=true`, Pydantic models for request bodies, and no secrets in logs. A PR that weakens one of these needs a strong reason and a test.
- New settings go in `api/config.py`, `.env.example` and the README configuration table.
