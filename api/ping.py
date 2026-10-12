import ipaddress
import subprocess
import sys
import re
from api.logger import logger
from api.targets import check_target


def _ping_command(ip: str) -> str:
    # macOS ping is IPv4 only
    if sys.platform == "darwin" and ipaddress.ip_address(ip).version == 6:
        return "ping6"
    return "ping"


def ping_host(host: str, count: int = 4) -> dict:
    # Re-check at ping time and ping the checked IP (DNS rebinding)
    ip = check_target(host)

    logger.info(f"Ping started: {host} ({ip})")

    try:
        result = subprocess.run(
            [_ping_command(ip), "-c", str(count), ip],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout

        # --- Parse packet loss ---
        loss_match = re.search(r"(\d+\.?\d*)% packet loss", output)
        packet_loss = float(loss_match.group(1)) if loss_match else 100.0

        # --- Parse packets sent/received ---
        packets_match = re.search(r"(\d+) packets transmitted, (\d+) received", output)
        packets_sent = int(packets_match.group(1)) if packets_match else count
        packets_received = int(packets_match.group(2)) if packets_match else 0

        # --- Parse average latency ---
        rtt_match = re.search(r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms", output)
        latency_ms = float(rtt_match.group(1)) if rtt_match else None

        reachable = packet_loss < 100.0

        logger.info(
            f"Ping complete: {host} | reachable={reachable} | "
            f"latency={latency_ms}ms | loss={packet_loss}%"
        )

        return {
            "host": host,
            "reachable": reachable,
            "latency_ms": latency_ms,
            "packets_sent": packets_sent,
            "packets_received": packets_received,
            "packet_loss_percent": packet_loss
        }

    except subprocess.TimeoutExpired:
        logger.error(f"Ping timeout: {host}")
        return {
            "host": host,
            "reachable": False,
            "latency_ms": None,
            "packets_sent": count,
            "packets_received": 0,
            "packet_loss_percent": 100.0
        }

    except Exception as e:
        logger.error(f"Ping error: {host} | {e}")
        return {
            "host": host,
            "reachable": False,
            "latency_ms": None,
            "packets_sent": count,
            "packets_received": 0,
            "packet_loss_percent": 100.0
        }