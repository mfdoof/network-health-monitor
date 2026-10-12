# Roadmap

From a hosted demo to an open-source tool you run locally. One step = one commit.

## Decisions
- **Open source, local only.** No public hosting. The maintainer's instance runs on a homelab, reachable over LAN and VPN only.
- **LLM-agnostic.** One OpenAI-compatible client set with `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_MODEL`. Groq is the documented default. OpenRouter and local Ollama are alternatives.
- **Redaction on by default.** Private IPs and internal hostnames are swapped for placeholders before anything reaches a cloud LLM.
- **Private targets blocked by default.** Set `ALLOW_PRIVATE_TARGETS=true` to scan your own LAN.
- **License:** MIT.
- **Out of scope for now:** persistent storage, in-app login.

---

## Phase 1: Security

- [x] **1. Block private targets by resolved IP**
  - New `api/targets.py`: resolve the host (IPv4 + IPv6), reject it if *any* address is private, loopback, link-local (incl. `169.254.169.254`), CGNAT `100.64.0.0/10`, multicast, reserved or unspecified. Use the `ipaddress` module.
  - Setting `ALLOW_PRIVATE_TARGETS` (default `false`).
  - Check on add **and** again at scan and ping time. Scan and ping the checked IP, not the hostname.
  - Remove `BLACKLISTED_HOSTS` (replaced by the range checks).
  - Check: `localhost`, `10.0.0.5`, `::1` and a hostname that resolves to a private IP are all rejected. `scanme.nmap.org` is allowed.

- [x] **2. Input validation**
  - Pydantic model for the `/api/dns/analyze` body (no raw `request.json()`).
  - Scan ports: 1–65535, max 20 per request, no duplicates.
  - Validate the DNS lookup `target` (hostname or IP, ≤ 253 chars).
  - Reject hosts that start with `-` (stops them being read as `ping` options).
  - Check: bad bodies return 422, not 500.

- [x] **3. Config and small fixes**
  - `CORS_ORIGINS` setting (default `http://localhost:5173`). Remove the hardcoded `doof.quest`.
  - `TRUST_PROXY` setting: read the client IP from `X-Forwarded-For` only when it's on, so rate limits work behind a proxy.
  - Fix the request-size middleware: it raises `HTTPException` in middleware (that gives a 500). Return a `JSONResponse(413)` instead.
  - Make `ping.py` match the README's OS support (Linux, macOS, Windows), or trim the README to Linux and macOS.
  - Check: the app starts with only `.env.example` copied, and the README endpoints table matches the code.

## Phase 2: AI

- [x] **4. Provider-agnostic LLM client**
  - New `api/llm.py`: `llm_complete(prompt) -> str` using `POST {LLM_BASE_URL}/chat/completions` through `httpx`.
  - Settings: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT` (default 30s).
  - `analyzer.py` calls `llm_complete`. Delete the duplicated Ollama calls. Keep the prompts.
  - Handle errors: 401 ("check API key"), 429 ("rate limited, try later"), timeout, not configured.
  - `GET /api/config` returns `{llm_enabled, provider_host, model}`. Never the key.
  - Check: works with Groq and with local Ollama (`http://localhost:11434/v1`).

- [ ] **5. Redaction**
  - New `api/redact.py`: swap private IPs and the scanned hostname for placeholders (`HOST_A`, `10.x.x.x → PRIVATE_IP_1`) and keep a map to restore them in the reply.
  - Setting `LLM_REDACT` (default `true`).
  - Check: a test proves no private IP or the original hostname appears in the outgoing prompt.

- [ ] **6. Frontend**
  - Hide or disable Analyze when `llm_enabled` is false, and say why.
  - Show the provider and model in the top bar.
  - Show the API's error messages instead of raw text.

## Phase 3: Open-source readiness

- [ ] **7. Tests** (`pytest`, `tests/`)
  - Target validation, input models, redaction, and the LLM client with a mocked HTTP response (`respx` or `httpx.MockTransport`).
  - No real network calls in tests.

- [ ] **8. Docker**
  - `Dockerfile` for the API (slim Python, non-root user). The `client` builds to static files served by an nginx container.
  - `compose.yaml`: `api` + `web`, `.env` passed through, ports bound to `127.0.0.1` by default.
  - Check: `docker compose up` gives a working app on a fresh machine.

- [ ] **9. CI** (`.github/workflows/ci.yml`)
  - On push and PR: `ruff`, `pytest`, `pip-audit`, `npm ci`, `npm run lint`, `npm run build`, `npm audit --audit-level=high`.

- [ ] **10. Docs**
  - README in standard order: title + one-line description, screenshot, features, quick start (Docker, then manual), configuration table, LLM providers (Groq, OpenRouter, Ollama), security model, limitations, contributing, license.
  - Add `LICENSE` (MIT), `SECURITY.md` (how to report, what's in scope), `CONTRIBUTING.md` (setup, run tests, PR rules).
  - Check provider free limits against each provider's own docs before writing them.

## Phase 4: Deploy and showcase

- [ ] **11. Homelab instance.** An LXC with Docker behind the existing reverse proxy, LAN and VPN only, `ALLOW_PRIVATE_TARGETS=true`.
- [ ] **12. Retire the old hosting docs.** Archive the `selfhosted-web-server` repo or mark it retired, with a link here.
- [ ] **13. Portfolio.** Screenshots and a GIF, a project page with the architecture and security choices.
