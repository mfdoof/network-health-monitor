# Network Health Monitor

A self-hosted dashboard for ping, TCP port scans, DNS lookups and LLM-written diagnostic summaries.

[![CI](https://github.com/mfdoof/network-health-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/mfdoof/network-health-monitor/actions/workflows/ci.yml)

## Features

- Ping hosts and see latency and packet loss
- TCP connect scan of up to 20 chosen ports per host
- DNS lookups: A, AAAA, MX and NS for hostnames, PTR for IPs
- AI diagnostic summaries from any OpenAI-compatible API (Groq, OpenRouter, local Ollama)
- IPs and hostnames redacted before anything reaches the LLM
- Private, loopback and cloud-metadata targets blocked by default

## Quick start (Docker)

```bash
git clone https://github.com/mfdoof/network-health-monitor.git && cd network-health-monitor
cp .env.example .env    # add LLM_API_KEY to enable AI analysis
docker compose up -d --build
```

Open http://localhost:8080. Stop it with `docker compose down`.

## Manual setup

Needs Python 3.14 and Node.js 24 (the versions CI and Docker use).

Backend, from the repo root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r api/requirements.txt
cp .env.example .env
uvicorn api.main:app --host 127.0.0.1 --port 8000 --no-proxy-headers
```

Frontend, in a second terminal:

```bash
cd client
npm ci
npm run dev
```

Open http://localhost:5173. API docs are at http://localhost:8000/docs.

## Configuration

Copy `.env.example` to `.env` and edit it. "Default" is the value used when a setting is missing.

| Setting | In `.env.example` | Default | Description |
|---|---|---|---|
| `MAX_REQUEST_SIZE` | `1024` | `1024` | Max request body in bytes |
| `SCAN_PORTS` | `21,22,25,80,443,3306,3389,5432,6379,8080` | same | Ports scanned when a request sends an empty port list |
| `ALLOW_PRIVATE_TARGETS` | `false` | `false` | Allow private, loopback, link-local, CGNAT and other non-public targets |
| `CORS_ORIGINS` | `http://localhost:5173` | same | Comma-separated origins allowed to call the API |
| `TRUST_PROXY` | `false` | `false` | Use the last `X-Forwarded-For` address as the client IP for rate limits. Only enable behind one reverse proxy that sets it (Docker Compose turns it on) |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | empty | OpenAI-compatible API base URL. Empty disables AI analysis |
| `LLM_API_KEY` | empty | empty | API key, sent as a Bearer token. Not needed for local Ollama |
| `LLM_MODEL` | `openai/gpt-oss-120b` | empty | Model name. Empty disables AI analysis |
| `LLM_TIMEOUT` | `30` | `30` | Seconds to wait for the LLM |
| `LLM_REDACT` | `true` | `true` | Replace IPs and hostnames with placeholders (`IP_1`, `HOST_1`) before sending data to the LLM. Only `false` turns it off |
| `WEB_BIND` | `127.0.0.1` | `127.0.0.1` | Docker Compose only: host address for the web container |
| `WEB_PORT` | `8080` | `8080` | Docker Compose only: host port for the web container |
| `TRUSTED_PROXY_IP` | empty | `127.0.0.1` | Docker Compose only: IP of a reverse proxy in front of the web container. Its `X-Forwarded-For` is trusted so each client gets its own rate limit. Empty means no proxy |

## LLM providers

Any OpenAI-compatible `/chat/completions` API works. Free tiers and rate limits change, so check each provider's own page.

**Groq** (default): [API keys](https://console.groq.com/keys), [models](https://console.groq.com/docs/models), [rate limits](https://console.groq.com/docs/rate-limits)

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=your-groq-key
LLM_MODEL=openai/gpt-oss-120b
```

**OpenRouter**: [quickstart](https://openrouter.ai/docs/quickstart), [models](https://openrouter.ai/models) (free variants end in `:free`), [rate limits](https://openrouter.ai/docs/api/reference/limits)

```env
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your-openrouter-key
LLM_MODEL=openai/gpt-oss-120b
```

**Local Ollama**: [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility). No key, and no data leaves your machine. Run `ollama pull llama3.2` first.

```env
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=
LLM_MODEL=llama3.2
```

When the API runs in Docker, `localhost` is the container itself, so point `LLM_BASE_URL` at your host's address instead.

## Security model

- **Private targets blocked by default.** Hosts are checked by resolved IP, not by name. Private, loopback, link-local (including `169.254.169.254`), CGNAT, multicast and reserved ranges are rejected if *any* address matches. The name is resolved again at scan and ping time and the checked IP is used, which stops DNS rebinding. Set `ALLOW_PRIVATE_TARGETS=true` to scan your own LAN.
- **Redaction on by default.** Every IP and hostname is swapped for a placeholder before the prompt is sent, and the real values are put back in the reply.
- **Rate limits per client IP:** 10/min for scan, ping and DNS lookup; 5/min for AI analysis.
- **No authentication.** Anyone who can reach the app can use it to scan. Keep it on localhost, your LAN or a VPN. Don't expose it to the internet.

## Limitations

- Hosts and results are kept in memory and lost on restart.
- Linux and macOS only (ping output is parsed for those two). The Docker image is Linux.
- No login or user accounts.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Report vulnerabilities as described in [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
