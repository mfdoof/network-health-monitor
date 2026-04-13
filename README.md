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

### 2. Ollama
Download from https://ollama.com
After installing, open a terminal and run: `` ollama pull llama3.2 ``

Then start Ollama: `` ollama serve ``

---

## Installation

Double click `install.bat`.

It will:
- Set PowerShell execution policy for the current user
- Create a Python virtual environment
- Install all dependencies from `requirements.txt`
- Verify Ollama is running

---

## Running the App

Double click `run.bat`.

Then open your browser and go to:  http://localhost:8000/static/index.html

Press `CTRL+C` in the terminal to stop the server.

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

## Security Measures

| # | Measure | Details |
|---|---|---|
| 1 | Input validation | Rejects invalid hostnames and IPs with 400 |
| 2 | Rate limiting | 10/min on scan, 5/min on analyze |
| 3 | CORS restriction | Localhost origins only |
| 4 | Config via .env | No sensitive values hardcoded |
| 5 | Port scope restriction | Only scans user-selected allowed ports |
| 6 | Host blacklist | Blocks loopback and metadata addresses |
| 7 | Request size limiting | Blocks oversized payloads |

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
| AI Integration | Ollama, llama3.2 |
| Port Scanning | Python socket (TCP connect) |
| Rate Limiting | slowapi |
| Config | python-dotenv |
| Frontend | HTML, CSS, JavaScript |

---

## Known Limitations

- Host list resets on server restart (no persistent storage)
- Ollama must be running separately before starting the app
- AI analysis quality depends on Ollama response time

---

## Future Improvements

- Persistent storage with a database
- JWT authentication
- Docker containerization



