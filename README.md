# Network Monitor

[![CI](https://github.com/mfdoof/network-health-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/mfdoof/network-health-monitor/actions/workflows/ci.yml)

A locally-run network health monitoring dashboard built with FastAPI and Python.
Add hosts, scan their port availability, and get AI-generated diagnostic summaries
from any OpenAI-compatible LLM (Groq by default, or local Ollama).

---

## Prerequisites

These must be installed manually before running the app.

### 1. Python 3.10+

Download from https://python.org

During installation, check "Add Python to PATH".

### 2. Node.js v22+

Download from https://nodejs.org

### 3. An LLM (optional)

AI analysis needs an OpenAI-compatible API. Scan, ping and DNS work without one.

- **Groq** (default): create a key at https://console.groq.com/keys and put it in `LLM_API_KEY`.
- **Local Ollama**: install from https://ollama.com, run `ollama pull llama3.2`, and use the commented Ollama lines in `.env.example`.

---

## Installation

```bash
git clone https://github.com/mfdoof/network-health-monitor.git
cd network-monitor
```

Install backend dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r api/requirements.txt
```

Install frontend dependencies:

```bash
cd client
npm install
```

Copy the environment file and adjust as needed:

```bash
cp .env.example .env
```

---

## Running the App

Start the backend (from the project root):

```bash
source venv/bin/activate
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload --no-proxy-headers
```

Start the frontend (from the `client/` directory):

```bash
npm run dev
```

Then open your browser and go to: http://localhost:5173

Press `CTRL+C` in each terminal to stop.

---

## Usage

1. Select the ports you want to scan using the port toggle buttons
2. Enter a hostname or IP address and click **Add Host**
3. Click **Scan** on any host to check port availability
4. Click **Analyze** to get an AI diagnostic summary from the configured LLM

---

## Configuration

Copy `.env.example` to `.env` and adjust values as needed.

| Variable | Default | Description |
|---|---|---|
| LLM_BASE_URL | (empty) | OpenAI-compatible API base URL, e.g. `https://api.groq.com/openai/v1` or `http://localhost:11434/v1`. Empty disables AI analysis |
| LLM_API_KEY | (empty) | API key sent as a Bearer token. Not needed for local Ollama |
| LLM_MODEL | (empty) | Model name, e.g. `openai/gpt-oss-120b` (Groq) or `llama3.2` (Ollama). Empty disables AI analysis |
| LLM_TIMEOUT | 30 | Seconds to wait for the LLM |
| LLM_REDACT | true | Replace every IP and hostname with placeholders (`IP_1`, `HOST_1`) before sending data to the LLM, and restore them in the reply. Set to `false` to send data unchanged |
| SCAN_PORTS | 21,22,25,80,443,3306,3389,5432,6379,8080 | Ports scanned when a request sends an empty port list |
| MAX_REQUEST_SIZE | 1024 | Max request body size in bytes |
| ALLOW_PRIVATE_TARGETS | false | Allow private, loopback, link-local, CGNAT and other non-public IPs as targets |
| CORS_ORIGINS | http://localhost:5173 | Comma-separated origins allowed to call the API |
| TRUST_PROXY | false | Use the last `X-Forwarded-For` address as the client IP for rate limiting. Only enable behind a single reverse proxy that sets it |
| WEB_BIND | 127.0.0.1 | Docker Compose only: host address the web container binds to. Use `0.0.0.0` to expose it on your LAN |
| WEB_PORT | 8080 | Docker Compose only: host port for the web container |

---

## Authentication

### Local development

No authentication. The app is accessible at `http://localhost:5173` with no login required. Keep this instance off any public network.

### Hosted instance (doof.quest)

Access is protected by Cloudflare Zero Trust at the edge, before any request reaches the origin server.

- Access requires a verified email address on the allow list
- A one-time passcode is sent to that email on each login
- Sessions are managed via a signed JWT cookie issued by Cloudflare Access
- No unauthenticated request reaches the origin

There is no in-app login page. Authentication is handled entirely by Cloudflare.

---

## Security Measures

| # | Measure | Local | Hosted (doof.quest) |
|---|---|---|---|
| 1 | Input validation | ✓ | ✓ |
| 2 | Rate limiting | 10/min scan, 5/min analyze | 10/min scan, 5/min analyze |
| 3 | CORS restriction | `CORS_ORIGINS` (default localhost:5173) | https://doof.quest only |
| 4 | Config via .env | ✓ | ✓ |
| 5 | Port scope restriction | ✓ | ✓ |
| 6 | Non-public targets blocked by resolved IP | ✓ | ✓ |
| 7 | Request size limiting | ✓ | ✓ |
| 8 | Edge authentication | — | Cloudflare Zero Trust |
| 9 | Nginx rate limiting | — | general + expensive zones |
| 10 | Fail2ban | — | SSH + Nginx jails |

---

## Platform Notes

The backend runs on **Linux and macOS**. Windows is not supported (its `ping` uses different flags and output).

Ping runs as `ping -c 4 <ip>` (`ping6` for IPv6 on macOS). Results are parsed from stdout:

| Field | Linux | macOS |
|---|---|---|
| Packets received | `4 received` | `4 packets received` |
| RTT stats | `rtt min/avg/max/mdev = ...` | `round-trip min/avg/max/stddev = ...` |

If ping results look empty or wrong, the output patterns in `api/ping.py` are the first place to check.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Health check |
| GET | /api/hosts | List all monitored hosts |
| POST | /api/hosts | Add a host |
| DELETE | /api/hosts/{id} | Remove a host |
| POST | /api/hosts/{id}/scan | Scan ports on a host |
| GET | /api/hosts/{id}/ping | Ping a host |
| POST | /api/hosts/{id}/analyze | AI diagnostic of the last scan |
| GET | /api/config | AI status: `llm_enabled`, `provider_host`, `model` (never the key) |
| GET | /api/dns/lookup?target= | DNS lookup (forward for hostnames, PTR for IPs) |
| POST | /api/dns/analyze | Look up a target and return an AI diagnostic of the result |

Full interactive API docs available at: http://localhost:8000/docs

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | React, Vite |
| AI Integration | Any OpenAI-compatible API via httpx (Groq, OpenRouter, Ollama) |
| Port Scanning | Python socket (TCP connect) |
| Rate Limiting | slowapi |
| Config | python-dotenv |

---

## Known Limitations

- Host list resets on server restart (no persistent storage)
- AI analysis needs an LLM provider; quality and speed depend on the model you pick

---

## Future Improvements

- Persistent storage with a database
- In-app authentication with JWT (session management at the application layer)
- Docker containerization