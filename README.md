# Network Monitor

A locally-run network health monitoring dashboard built with FastAPI and Python.
Add hosts, scan their port availability, and get AI-generated diagnostic summaries
powered by Ollama running llama3.2 locally.

---

## Prerequisites

These must be installed manually before running the app.

### 1. Python 3.10+

Download from https://python.org

During installation, check "Add Python to PATH".

### 2. Node.js v22+

Download from https://nodejs.org

### 3. Ollama

Download from https://ollama.com

After installing, open a terminal and run:

```bash
ollama pull llama3.2
```

Then start Ollama:

```bash
ollama serve
```

---

## Installation

```bash
git clone https://github.com/mfdoof/network-health-monitor.git
cd network-monitor
```

Install backend dependencies:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
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
source venv/bin/activate        # Windows: venv\Scripts\activate
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
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
4. Click **Analyze** to get an AI diagnostic summary from Ollama

---

## Configuration

Copy `.env.example` to `.env` and adjust values as needed.

| Variable | Default | Description |
|---|---|---|
| OLLAMA_URL | http://localhost:11434 | Ollama server address |
| OLLAMA_MODEL | llama3.2 | Model to use for analysis |
| SCAN_PORTS | 22,80,443,3389,8080 | Default allowed ports |
| MAX_REQUEST_SIZE | 1024 | Max request body size in bytes |
| BLACKLISTED_HOSTS | 127.0.0.1,0.0.0.0,... | Hosts blocked from scanning |

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
| 3 | CORS restriction | localhost:5173 only | https://doof.quest only |
| 4 | Config via .env | ✓ | ✓ |
| 5 | Port scope restriction | ✓ | ✓ |
| 6 | Host blacklist | ✓ | ✓ |
| 7 | Request size limiting | ✓ | ✓ |
| 8 | Edge authentication | — | Cloudflare Zero Trust |
| 9 | Nginx rate limiting | — | general + expensive zones |
| 10 | Fail2ban | — | SSH + Nginx jails |

---

## Platform Notes

The ping implementation adapts to the host operating system at runtime. If you are running the backend on a different OS than the one it was developed on, be aware of the following differences.

### Ping flag

| OS | Count flag | Timeout flag | Timeout unit |
|---|---|---|---|
| Linux | `-c` | `-W` | seconds |
| macOS | `-c` | `-W` | milliseconds |
| Windows | `-n` | `-w` | milliseconds |

### Ping output format

Packet loss and round-trip time are parsed from stdout using OS-specific patterns.

| Field | Linux | macOS | Windows |
|---|---|---|---|
| Packets received | `4 received` | `4 packets received` | `Received = 4` |
| RTT stats | `rtt min/avg/max/mdev = ...` | `round-trip min/avg/max/stddev = ...` | `Average = 12ms` |

If ping results appear empty or malformed after moving the app to a different OS, the output patterns in `api/ping.py` are the first place to check.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Health check |
| GET | /hosts | List all monitored hosts |
| POST | /hosts | Add a host |
| DELETE | /hosts/{id} | Remove a host |
| GET | /hosts/{id}/scan | Scan ports on a host |
| POST | /hosts/{id}/analyze | AI diagnostic via Ollama |

Full interactive API docs available at: http://localhost:8000/docs

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | React, Vite |
| AI Integration | Ollama, llama3.2 |
| Port Scanning | Python socket (TCP connect) |
| Rate Limiting | slowapi |
| Config | python-dotenv |

---

## Known Limitations

- Host list resets on server restart (no persistent storage)
- Ollama must be running separately before starting the app
- AI analysis quality depends on Ollama response time

---

## Future Improvements

- Persistent storage with a database
- In-app authentication with JWT (session management at the application layer)
- Docker containerization