import socket
import subprocess

import pytest
from fastapi.testclient import TestClient

from api import analyzer, llm, main, targets

LLM_URL = "https://llm.test/v1"
LLM_KEY = "sk-test-not-a-real-key"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Fail loudly if anything tries a real DNS lookup or connection."""
    def blocked(*args, **kwargs):
        raise RuntimeError("Real network access in tests")

    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    """Known settings for every test, regardless of the local .env."""
    monkeypatch.setattr(targets, "ALLOW_PRIVATE_TARGETS", False)
    monkeypatch.setattr(analyzer, "LLM_REDACT", True)
    monkeypatch.setattr(llm, "LLM_BASE_URL", LLM_URL)
    monkeypatch.setattr(llm, "LLM_API_KEY", LLM_KEY)
    monkeypatch.setattr(llm, "LLM_MODEL", "test-model")
    monkeypatch.setattr(llm, "LLM_TIMEOUT", 1.0)
    monkeypatch.setattr(main.limiter, "enabled", False)
    main.hosts.clear()


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture
def fake_dns(monkeypatch):
    """
    Map hostnames (or IP literals) to the addresses getaddrinfo should return.
    Usage: fake_dns({"example.com": ["93.184.216.34"]})
    """
    table: dict[str, list[str]] = {}

    def getaddrinfo(host, *args, **kwargs):
        if host not in table:
            raise socket.gaierror(socket.EAI_NONAME, "not found")
        return [
            (socket.AF_INET6 if ":" in ip else socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))
            for ip in table[host]
        ]

    monkeypatch.setattr(targets.socket, "getaddrinfo", getaddrinfo)

    def set_records(mapping: dict[str, list[str]]) -> None:
        table.clear()
        table.update(mapping)

    return set_records


@pytest.fixture
def connections(monkeypatch):
    """Record every (host, port) the scanner tries; all ports report closed."""
    seen: list[tuple[str, int]] = []

    def is_port_open(host, port, timeout=1.0):
        seen.append((host, port))
        return port == 22

    monkeypatch.setattr("api.scanner.is_port_open", is_port_open)
    return seen


LINUX_PING_OUTPUT = """PING 45.33.32.156 (45.33.32.156) 56(84) bytes of data.

--- 45.33.32.156 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 152.101/153.402/155.012/1.110 ms
"""


@pytest.fixture
def ping_calls(monkeypatch):
    """Record ping argv lists and return canned Linux output."""
    calls: list[list[str]] = []

    def run(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout=LINUX_PING_OUTPUT, stderr="")

    monkeypatch.setattr("api.ping.subprocess.run", run)
    return calls


def add_host(client, host: str) -> str:
    r = client.post("/api/hosts", json={"host": host})
    assert r.status_code == 200, r.text
    return r.json()["entry"]["id"]
