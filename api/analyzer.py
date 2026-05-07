import httpx
from api.config import OLLAMA_URL, OLLAMA_MODEL
from api.logger import logger
import re


def build_prompt(scan_result: dict, ping_result: dict = None) -> str:
    logger.info(f"Scan result keys: {scan_result}")
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

    ping_section = ""
    if ping_result:
        reachable = ping_result.get("reachable")
        latency = ping_result.get("latency_ms")
        loss = ping_result.get("packet_loss_percent")
        packets_sent = ping_result.get("packets_sent")
        packets_received = ping_result.get("packets_received")
        ping_section = f"""
Ping results:
  Reachable: {reachable}
  Latency: {latency} ms
  Packet loss: {loss}%
  Packets sent/received: {packets_sent}/{packets_received}
"""

    return f"""You are a network diagnostic assistant for IT support.
    You must only use the data provided below. Do not infer, assume, or add information not present in the data.

    A port scan and optional ping were run on host: {host}

    Scan results:
    Host reachable (via scan): {is_up}
    Open ports: {describe_ports(open_ports)}
    Closed ports (within scanned set only): {describe_ports(closed_ports)}
    Note: only these ports were scanned — closed does not mean all other ports are blocked.
    {ping_section}
    Using only the data above, give a 2-3 sentence plain-English diagnostic summary. If open ports is "none", do not mention any ports as open. If the host is unreachable, focus on that. Then give one specific recommended action based strictly on the data.
    Do not use bullet points. Do not use markdown formatting.
    Do not include labels like "Recommended action:" in your response."""



async def analyze_scan(scan_result: dict, ping_result: dict = None) -> str:
    prompt = build_prompt(scan_result, ping_result)
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


def build_dns_prompt(dns_result: dict) -> str:
    target = dns_result["target"]
    lookup_type = dns_result["lookup_type"]

    if lookup_type == "reverse":
        ptr_records = dns_result.get("ptr_records", [])
        ptr_list = ", ".join(r["hostname"] for r in ptr_records) if ptr_records else "none"
        return f"""You are a network diagnostic assistant for IT support.

A reverse DNS lookup was run on IP: {target}
PTR records found: {ptr_list}

Explain in 2-3 plain-English sentences what this reverse DNS result indicates about the IP address and who likely operates it. Then give one recommended action.
Do not use bullet points. Do not use markdown formatting.
Do not include labels like "Recommended action:" in your response."""

    a_records = [r["address"] for r in dns_result.get("a_records", [])]
    aaaa_records = [r["address"] for r in dns_result.get("aaaa_records", [])]
    mx_records = [f"{r['host']} (priority {r['preference']})" for r in dns_result.get("mx_records", [])]
    ns_records = [r["nameserver"] for r in dns_result.get("ns_records", [])]
    errors = dns_result.get("errors", [])

    error_section = f"\nWarnings: {', '.join(errors)}" if errors else ""

    return f"""You are a network diagnostic assistant for IT support.

A DNS lookup was run on domain: {target}

DNS records found:
  A records (IPv4): {", ".join(a_records) or "none"}
  AAAA records (IPv6): {", ".join(aaaa_records) or "none"}
  MX records (mail servers): {", ".join(mx_records) or "none"}
  NS records (nameservers): {", ".join(ns_records) or "none"}
{error_section}
In 2-3 plain-English sentences, summarize what this DNS configuration tells you about the domain — including whether mail is configured, how many IPs it resolves to, and anything notable. Then give one recommended action.
Do not use bullet points. Do not use markdown formatting.
Do not include labels like "Recommended action:" in your response."""


async def analyze_dns(dns_result: dict) -> str:
    prompt = build_dns_prompt(dns_result)
    target = dns_result["target"]
    logger.info(f"DNS analyze requested: {target}")

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
            logger.info(f"DNS analyze complete: {target}")
            return raw

    except httpx.TimeoutException:
        logger.error(f"Ollama timeout for DNS analyze: {target}")
        return "AI analysis timed out. Ollama may be under load. Try again."

    except Exception as e:
        logger.error(f"Ollama unreachable: {str(e)}")
        return "AI analysis unavailable. Check Ollama is running."