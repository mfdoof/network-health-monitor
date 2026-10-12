# CLAUDE.md

Context for Claude Code in this repo. Read `docs/ROADMAP.md` before starting work.

## Project
Network Health Monitor: a self-hosted tool for ping, TCP port scans, DNS lookups and LLM-written diagnostic summaries.
- Backend: Python, FastAPI (`api/`)
- Frontend: React + Vite (`client/`)
- LLM: any OpenAI-compatible API (Groq by default, local Ollama works too)

Goal: an open-source project people run locally. It is **not** hosted publicly.

## Rules
- **Never run git.** Not even `git status` or `git diff`. The maintainer runs every git command. When a step is done, list the changed files and suggest a one-line commit message.
- **Never move, copy, rename or edit `.env`.** To run without its values, override the variables in the command; python-dotenv never replaces a variable that's already set. Example: `LLM_BASE_URL= LLM_API_KEY= LLM_MODEL= pytest`. Numeric settings (`LLM_TIMEOUT`, `MAX_REQUEST_SIZE`, `SCAN_PORTS`) can't be empty, so give them a value instead.
- **No AI attribution.** No `Co-Authored-By`, "Generated with" lines or similar in commits, code, comments or docs.
- One roadmap step at a time. Stop after each step so it can be reviewed and committed.
- Tick the step's box in `docs/ROADMAP.md` once its checks pass.
- Keep replies short and direct.

## Security defaults (do not weaken)
- Scan targets are checked by **resolved IP**, not by string. Private, loopback, link-local, CGNAT, multicast and reserved ranges are blocked unless `ALLOW_PRIVATE_TARGETS=true`.
- Resolve again at scan time and connect to the checked IP (DNS rebinding).
- All request bodies use Pydantic models. No raw `request.json()`.
- Data sent to the LLM is redacted by default (`LLM_REDACT=true`).
- Secrets come from `.env` only. Never commit `.env` or put real keys in examples.
- `ping` runs with an argument list, never `shell=True`.

## Commands
```bash
# backend (repo root)
python3 -m venv venv && source venv/bin/activate
pip install -r api/requirements.txt
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload --no-proxy-headers
pytest                      # after Phase 3 step 7

# frontend
cd client && npm install && npm run dev    # http://localhost:5173
npm run lint
```

## Style
- Python: type hints, small functions, `logger` from `api/logger.py` (no `print`).
- Config only in `api/config.py`. Every new setting also goes in `.env.example` and the README config table.
- User-facing errors are short and don't leak internals.
