import uuid
import re
import socket
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from api.config import MAX_REQUEST_SIZE, SCAN_PORTS
from api.logger import logger
from api.scanner import scan_host, is_blacklisted
from api.analyzer import analyze_scan, analyze_dns
from api.ping import ping_host
from api.dns_lookup import run_dns_lookup
from fastapi.staticfiles import StaticFiles

# --- App Setup ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Network Monitor")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1",
                   "http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

# --- Request Size Limiting ---
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        logger.error(f"Request too large: {content_length} bytes")
        raise HTTPException(status_code=413, detail="Request too large")
    return await call_next(request)

# --- In-Memory Storage ---
hosts = []

# --- Pydantic Model ---
class HostInput(BaseModel):
    host: str
    ports: list[int] = []

# --- Input Validation ---
def is_valid_host(host: str) -> bool:
    try:
        socket.inet_aton(host)
        return True
    except socket.error:
        pass
    pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return re.match(pattern, host) is not None

# --- Routes ---
@app.get("/")
def root():
    logger.info("Health check called")
    return {"status": "Network Monitor running"}


@app.get("/hosts")
def get_hosts():
    logger.info("Host list requested")
    return {"hosts": hosts}


@app.post("/hosts")
def add_host(data: HostInput):
    host = data.host.strip()

    if not is_valid_host(host):
        logger.error(f"Invalid host rejected: {host}")
        raise HTTPException(status_code=400, detail="Invalid hostname or IP address")

    if is_blacklisted(host):
        logger.error(f"Blacklisted host rejected: {host}")
        raise HTTPException(status_code=403, detail="This host is not allowed")

    if any(h["host"] == host for h in hosts):
        raise HTTPException(status_code=409, detail="Host already exists")

    entry = {
        "id": str(uuid.uuid4())[:8],
        "host": host,
        "ports": data.ports,
        "last_scan": None,
        "last_ping": None
    }
    hosts.append(entry)
    logger.info(f"Host added: {host}")
    return {"message": "Host added", "entry": entry}


@app.delete("/hosts/{host_id}")
def delete_host(host_id: str):
    for i, h in enumerate(hosts):
        if h["id"] == host_id:
            removed = hosts.pop(i)
            logger.info(f"Host removed: {removed['host']}")
            return {"message": "Host removed", "host": removed["host"]}
    raise HTTPException(status_code=404, detail="Host not found")


@app.get("/hosts/{host_id}/scan")
@limiter.limit("10/minute")
def scan(host_id: str, request: Request):
    for h in hosts:
        if h["id"] == host_id:
            try:
                result = scan_host(h["host"], h["ports"] if h["ports"] else None)
                h["last_scan"] = result
                return result
            except ValueError as e:
                raise HTTPException(status_code=403, detail=str(e))
    raise HTTPException(status_code=404, detail="Host not found")


@app.get("/hosts/{host_id}/ping")
@limiter.limit("10/minute")
def ping(host_id: str, request: Request):
    for h in hosts:
        if h["id"] == host_id:
            result = ping_host(h["host"])
            h["last_ping"] = result
            return result
    raise HTTPException(status_code=404, detail="Host not found")


@app.post("/hosts/{host_id}/analyze")
@limiter.limit("5/minute")
async def analyze(host_id: str, request: Request):
    for h in hosts:
        if h["id"] == host_id:
            if h["last_scan"] is None:
                raise HTTPException(
                    status_code=400,
                    detail="Run a scan first before analyzing"
                )
            result = await analyze_scan(h["last_scan"], h.get("last_ping"))
            return {"host": h["host"], "analysis": result}
    raise HTTPException(status_code=404, detail="Host not found")


@app.get("/dns/lookup")
@limiter.limit("10/minute")
async def dns_lookup(target: str, request: Request):
    result = run_dns_lookup(target)
    return result


@app.post("/dns/analyze")
@limiter.limit("5/minute")
async def dns_analyze(request: Request):
    body = await request.json()
    result = await analyze_dns(body["dns_result"])
    return {"analysis": result}