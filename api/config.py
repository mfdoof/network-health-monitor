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

BLACKLISTED_HOSTS = os.getenv(
    "BLACKLISTED_HOSTS",
    "127.0.0.1,0.0.0.0,localhost,169.254.169.254,::1,0.0.0.0/8,10.0.0.1,192.168.0.1,192.168.1.1,metadata.google.internal"
).split(",")

