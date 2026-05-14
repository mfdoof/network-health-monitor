import subprocess
import re
from api.logger import logger


def ping_host(host: str, count: int = 4) -> dict:

    logger.info(f"Ping started: {host}")

    try:
        result = subprocess.run(
            ["ping", "-c", str(count), host],
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