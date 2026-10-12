import uuid
import re
import ipaddress
from typing import Annotated
from fastapi import FastAPI, HTTPException, Request, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import AfterValidator, BaseModel, Field, field_validator
from api.config import MAX_REQUEST_SIZE, CORS_ORIGINS, TRUST_PROXY
from api.logger import logger
from api.scanner import scan_host
from api.targets import check_target, TargetError, TargetNotAllowed
from api.analyzer import analyze_scan, analyze_dns
from api.llm import LLMError, llm_enabled, model_name, provider_host
from api.ping import ping_host
from api.dns_lookup import run_dns_lookup

# --- App Setup ---
def get_client_ip(request: Request) -> str:
    # Behind a reverse proxy the peer is the proxy, so use the address it appended.
    # The last entry is the one our proxy added; earlier entries are client-supplied.
    if TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for", "")
        last = forwarded.split(",")[-1].strip()
        if last:
            return last
    return get_remote_address(request)

limiter = Limiter(key_func=get_client_ip)
app = FastAPI(title="Network Monitor")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

# --- Request Size Limiting ---
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    # Raising HTTPException in middleware becomes a 500, so return the response directly
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            size = int(content_length)
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length"})
        if size > MAX_REQUEST_SIZE:
            logger.error(f"Request too large: {size} bytes")
            return JSONResponse(status_code=413, content={"detail": "Request too large"})
    return await call_next(request)

# --- In-Memory Storage ---
hosts = []

# --- Input Validation ---
MAX_HOST_LENGTH = 253
MAX_SCAN_PORTS = 20


def is_valid_host(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return re.match(pattern, host) is not None


def validate_host(host: str) -> str:
    host = host.strip()
    if not host or len(host) > MAX_HOST_LENGTH:
        raise ValueError(f"Host must be 1-{MAX_HOST_LENGTH} characters")
    # A leading "-" could be read as a ping option
    if host.startswith("-"):
        raise ValueError("Host must not start with '-'")
    if not is_valid_host(host):
        raise ValueError("Invalid hostname or IP address")
    return host


HostStr = Annotated[str, AfterValidator(validate_host)]
Port = Annotated[int, Field(ge=1, le=65535)]

# --- Pydantic Models ---
class HostInput(BaseModel):
    host: HostStr

class ScanInput(BaseModel):
    ports: list[Port] = Field(max_length=MAX_SCAN_PORTS)

    @field_validator("ports")
    @classmethod
    def no_duplicates(cls, ports: list[int]) -> list[int]:
        if len(set(ports)) != len(ports):
            raise ValueError("Duplicate ports")
        return ports

class DnsAnalyzeInput(BaseModel):
    target: HostStr

def target_http_error(e: TargetError) -> HTTPException:
    status = 403 if isinstance(e, TargetNotAllowed) else 400
    return HTTPException(status_code=status, detail=str(e))

# --- Router ---
router = APIRouter(prefix="/api")

# --- Health Check (on app directly, not under /api) ---
@app.get("/")
def root():
    logger.info("Health check called")
    return {"status": "Network Monitor running"}

# --- Host Routes ---
@router.get("/hosts")
def get_hosts():
    logger.info("Host list requested")
    return {"hosts": hosts}


@router.post("/hosts")
def add_host(data: HostInput):
    host = data.host

    try:
        check_target(host)
    except TargetError as e:
        logger.error(f"Target rejected: {host} | {e}")
        raise target_http_error(e)

    if any(h["host"] == host for h in hosts):
        raise HTTPException(status_code=409, detail="Host already exists")

    entry = {
        "id": str(uuid.uuid4())[:8],
        "host": host,
        "ports": [],
        "last_scan": None,
        "last_ping": None
    }
    hosts.append(entry)
    logger.info(f"Host added: {host}")
    return {"message": "Host added", "entry": entry}


@router.delete("/hosts/{host_id}")
def delete_host(host_id: str):
    for i, h in enumerate(hosts):
        if h["id"] == host_id:
            removed = hosts.pop(i)
            logger.info(f"Host removed: {removed['host']}")
            return {"message": "Host removed", "host": removed["host"]}
    raise HTTPException(status_code=404, detail="Host not found")


@router.post("/hosts/{host_id}/scan")
@limiter.limit("10/minute")
def scan(host_id: str, data: ScanInput, request: Request):
    for h in hosts:
        if h["id"] == host_id:
            try:
                result = scan_host(h["host"], data.ports)
                h["last_scan"] = result
                return result
            except TargetError as e:
                raise target_http_error(e)
    raise HTTPException(status_code=404, detail="Host not found")


@router.get("/hosts/{host_id}/ping")
@limiter.limit("10/minute")
def ping(host_id: str, request: Request):
    for h in hosts:
        if h["id"] == host_id:
            try:
                result = ping_host(h["host"])
            except TargetError as e:
                raise target_http_error(e)
            h["last_ping"] = result
            return result
    raise HTTPException(status_code=404, detail="Host not found")


@router.post("/hosts/{host_id}/analyze")
@limiter.limit("5/minute")
async def analyze(host_id: str, request: Request):
    for h in hosts:
        if h["id"] == host_id:
            if h["last_scan"] is None:
                raise HTTPException(
                    status_code=400,
                    detail="Run a scan first before analyzing"
                )
            try:
                result = await analyze_scan(h["last_scan"], h.get("last_ping"))
            except LLMError as e:
                raise HTTPException(status_code=e.status_code, detail=str(e))
            return {"host": h["host"], "analysis": result}
    raise HTTPException(status_code=404, detail="Host not found")

@router.get("/config")
def get_config():
    return {
        "llm_enabled": llm_enabled(),
        "provider_host": provider_host(),
        "model": model_name(),
    }

# --- DNS Routes ---
@router.get("/dns/lookup")
@limiter.limit("10/minute")
async def dns_lookup(target: Annotated[HostStr, Query()], request: Request):
    result = run_dns_lookup(target)
    return result


@router.post("/dns/analyze")
@limiter.limit("5/minute")
async def dns_analyze(data: DnsAnalyzeInput, request: Request):
    # Look up again server-side rather than trusting a client-supplied result
    dns_result = run_dns_lookup(data.target)
    try:
        result = await analyze_dns(dns_result)
    except LLMError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return {"analysis": result}


# --- Register Router ---
app.include_router(router)