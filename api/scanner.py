import socket
from api.config import SCAN_PORTS, BLACKLISTED_HOSTS
from api.logger import logger
from concurrent.futures import ThreadPoolExecutor, as_completed


def is_blacklisted(host: str) -> bool:
    return host in BLACKLISTED_HOSTS


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except (socket.timeout, socket.error):
        return False


def is_host_up(host: str) -> bool:
    for port in [80, 443, 22]:
        if is_port_open(host, port):
            return True
    return False


def scan_host(host: str, ports: list = None) -> dict:
    if is_blacklisted(host):
        logger.error(f"Blocked scan attempt on blacklisted host: {host}")
        raise ValueError(f"Host {host} is not allowed to be scanned")

    logger.info(f"Scan started: {host}")

    open_ports = []
    closed_ports = []
    ports_to_scan = ports if ports else SCAN_PORTS

    def check_port(port):
        return port, is_port_open(host, port)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_port, port): port for port in ports_to_scan}
        for future in as_completed(futures):
            port, is_open = future.result()
            if is_open:
                open_ports.append(port)
            else:
                closed_ports.append(port)

    up = is_host_up(host)
    open_ports.sort()
    closed_ports.sort()

    result = {
        "host": host,
        "is_up": up,
        "open_ports": open_ports,
        "closed_ports": closed_ports
    }

    logger.info(f"Scan complete: {host} | up={up} | open={open_ports} | closed={closed_ports}")

    return result


if __name__ == "__main__":
    result = scan_host("google.com")
    print(result)