from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "1024"))

SCAN_PORTS = [
    int(p) for p in os.getenv(
        "SCAN_PORTS",
        "21,22,25,80,443,3306,3389,5432,6379,8080"
    ).split(",")
]

ALLOW_PRIVATE_TARGETS = os.getenv("ALLOW_PRIVATE_TARGETS", "false").strip().lower() == "true"
