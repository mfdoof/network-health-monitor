import httpx
from api.config import OLLAMA_URL, OLLAMA_MODEL
from api.logger import logger
import re


def build_prompt(scan_result: dict) -> str:
    host = scan_result["host"]
    is_up = scan_result["is_up"]
    open_ports = scan_result["open_ports"]
    closed_ports = scan_result["closed_ports"]

    port_descriptions = {
        22: "SSH",
        80: "HTTP",
        443: "HTTPS",
        3389: "RDP",
        8080: "HTTP-ALT"
    }

    def describe_ports(ports):
        if not ports:
            return "none"
        return ", ".join(f"{p} ({port_descriptions.get(p, 'unknown')})" for p in ports)

    return f"""You are a network diagnostic assistant for IT support.

A scan was run on host: {host}
Host reachable: {is_up}
Open ports: {describe_ports(open_ports)}
Closed ports: {describe_ports(closed_ports)}

Give a 2-3 sentence plain-English diagnostic summary and one recommended action.
Do not use bullet points. Do not use markdown formatting.
Do not include labels like "Recommended action:" in your response."""

async def analyze_scan(scan_result: dict) -> str:
    prompt = build_prompt(scan_result)

    logger.info(f"Analyze requested: {scan_result['host']}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            raw = response.json()["response"].strip()
            result = re.sub(r'(?i)recommended action[:\s]*', '', raw).strip()
            logger.info(f"Analyze complete: {scan_result['host']}")
            return result

    except httpx.TimeoutException:
        logger.error(f"Ollama timeout for host: {scan_result['host']}")
        return "AI analysis timed out. Ollama may be under load. Try again."

    except Exception as e:
        logger.error(f"Ollama unreachable: {str(e)}")
        return "AI analysis unavailable. Check Ollama is running."