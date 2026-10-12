from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI-compatible LLM. Leave LLM_BASE_URL or LLM_MODEL empty to disable AI analysis.
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "").strip()
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30"))
# Swap IPs and hostnames for placeholders before anything reaches the LLM
LLM_REDACT = os.getenv("LLM_REDACT", "true").strip().lower() != "false"
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "1024"))

SCAN_PORTS = [
    int(p) for p in os.getenv(
        "SCAN_PORTS",
        "21,22,25,80,443,3306,3389,5432,6379,8080"
    ).split(",")
]

ALLOW_PRIVATE_TARGETS = os.getenv("ALLOW_PRIVATE_TARGETS", "false").strip().lower() == "true"

CORS_ORIGINS = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]

TRUST_PROXY = os.getenv("TRUST_PROXY", "false").strip().lower() == "true"
