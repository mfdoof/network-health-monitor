import pytest

from tests.conftest import add_host


@pytest.mark.parametrize("body", [
    {},
    {"host": 123},
    {"host": ""},
    {"host": "-c1"},
    {"host": "--help.example.com"},
    {"host": "not a host"},
    {"host": "a" * 254},
    {"host": "under_score.com"},
], ids=["missing", "number", "empty", "dash", "dash-domain", "spaces", "too-long", "underscore"])
def test_add_host_rejects_bad_input(client, body):
    assert client.post("/api/hosts", json=body).status_code == 422


def test_add_host_rejects_invalid_json(client):
    r = client.post("/api/hosts", content=b"not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422


def test_add_host_strips_whitespace(client, fake_dns):
    fake_dns({"scanme.example.com": ["45.33.32.156"]})
    r = client.post("/api/hosts", json={"host": "  scanme.example.com  "})
    assert r.status_code == 200
    assert r.json()["entry"]["host"] == "scanme.example.com"


@pytest.mark.parametrize("body", [
    {},
    {"ports": "22"},
    {"ports": ["abc"]},
    {"ports": [0]},
    {"ports": [65536]},
    {"ports": [-1]},
    {"ports": [22, 22]},
    {"ports": list(range(1, 22))},
], ids=["missing", "string", "non-int", "zero", "too-high", "negative", "duplicate", "21-ports"])
def test_scan_rejects_bad_ports(client, fake_dns, connections, body):
    fake_dns({"scanme.example.com": ["45.33.32.156"]})
    host_id = add_host(client, "scanme.example.com")
    assert client.post(f"/api/hosts/{host_id}/scan", json=body).status_code == 422
    assert connections == []


def test_scan_accepts_twenty_ports(client, fake_dns, connections):
    fake_dns({"scanme.example.com": ["45.33.32.156"]})
    host_id = add_host(client, "scanme.example.com")
    r = client.post(f"/api/hosts/{host_id}/scan", json={"ports": list(range(1, 21))})
    assert r.status_code == 200


@pytest.mark.parametrize("query", ["", "?target=", "?target=-x", "?target=bad%20name", "?target=" + "a" * 250 + ".com"])
def test_dns_lookup_rejects_bad_target(client, query):
    assert client.get(f"/api/dns/lookup{query}").status_code == 422


@pytest.mark.parametrize("body", [
    {},
    {"target": ""},
    {"target": "-x"},
    {"target": 5},
    {"dns_result": {"lookup_type": "forward", "target": "example.com"}},
], ids=["missing", "empty", "dash", "number", "old-style-body"])
def test_dns_analyze_rejects_bad_body(client, body):
    assert client.post("/api/dns/analyze", json=body).status_code == 422


def test_oversized_body_returns_413(client):
    r = client.post("/api/hosts", json={"host": "a" * 2000})
    assert r.status_code == 413
    assert r.json() == {"detail": "Request too large"}
