import json
import re

import httpx
import pytest
import respx

from api import analyzer, targets
from api.redact import Redactor
from tests.conftest import LLM_URL, add_host

COMPLETIONS = f"{LLM_URL}/chat/completions"

DNS_RESULT = {
    "lookup_type": "forward",
    "target": "corp.example.com",
    "a_records": [{"address": "93.184.216.34", "ttl": 300}, {"address": "10.0.0.5", "ttl": 300}],
    "aaaa_records": [{"address": "2606:2800:220:1::248", "ttl": 300}],
    "mx_records": [{"host": "mail.corp.example.com", "preference": 10, "ttl": 300}],
    "ns_records": [{"nameserver": "ns1.dnsprovider.net", "ttl": 300}, {"nameserver": "ns2.dnsprovider.net", "ttl": 300}],
    "errors": ["Lookup of corp.example.com was slow"],
}
DNS_REAL_VALUES = [
    "corp.example.com", "93.184.216.34", "10.0.0.5", "2606:2800:220:1::248",
    "mail.corp.example.com", "ns1.dnsprovider.net", "ns2.dnsprovider.net",
]


def echo_placeholders(request: httpx.Request) -> httpx.Response:
    """Fake LLM: reply with every placeholder it saw in the data section."""
    prompt = json.loads(request.content)["messages"][0]["content"]
    data = prompt.split("Now analyze the following")[1]
    seen = sorted(set(re.findall(r"\b(?:IP|HOST)_\d+\b", data)))
    return httpx.Response(200, json={"choices": [{"message": {"content": "Seen: " + ", ".join(seen)}}]})


def outgoing_prompt(route) -> str:
    return json.loads(route.calls.last.request.content)["messages"][0]["content"]


@pytest.fixture
def dns_result(monkeypatch):
    monkeypatch.setattr("api.main.run_dns_lookup", lambda target: json.loads(json.dumps(DNS_RESULT)))


# --- Outgoing request and restored reply ---

@respx.mock
def test_dns_analyze_redacts_every_value(client, dns_result):
    route = respx.post(COMPLETIONS).mock(side_effect=echo_placeholders)
    r = client.post("/api/dns/analyze", json={"target": "corp.example.com"})
    assert r.status_code == 200

    prompt = outgoing_prompt(route).lower()
    for value in DNS_REAL_VALUES:
        assert value.lower() not in prompt, value

    reply = r.json()["analysis"]
    for value in DNS_REAL_VALUES:
        assert value in reply, value
    assert not re.search(r"\b(?:IP|HOST)_\d+\b", reply)


@respx.mock
def test_scan_analyze_redacts_host(client, fake_dns, connections, monkeypatch):
    monkeypatch.setattr(targets, "ALLOW_PRIVATE_TARGETS", True)
    for host in ["scanme.example.com", "10.0.0.5"]:
        fake_dns({host: ["10.0.0.5"] if host == "10.0.0.5" else ["45.33.32.156"]})
        host_id = add_host(client, host)
        assert client.post(f"/api/hosts/{host_id}/scan", json={"ports": [22, 80]}).status_code == 200

        route = respx.post(COMPLETIONS).mock(side_effect=echo_placeholders)
        r = client.post(f"/api/hosts/{host_id}/analyze")
        assert r.status_code == 200
        assert host not in outgoing_prompt(route)
        assert r.json()["analysis"] == f"Seen: {host}"


@respx.mock
def test_target_in_prompt_examples_is_redacted_too(client, monkeypatch):
    # "example.com" also appears in the prompt's few-shot examples
    monkeypatch.setattr("api.main.run_dns_lookup", lambda target: {
        "lookup_type": "forward", "target": "example.com", "a_records": [], "aaaa_records": [],
        "mx_records": [], "ns_records": [], "errors": [],
    })
    route = respx.post(COMPLETIONS).mock(side_effect=echo_placeholders)
    client.post("/api/dns/analyze", json={"target": "example.com"})
    assert "example.com" not in outgoing_prompt(route).lower()


@respx.mock
def test_redaction_off_sends_data_unchanged(client, dns_result, monkeypatch):
    monkeypatch.setattr(analyzer, "LLM_REDACT", False)
    route = respx.post(COMPLETIONS).mock(side_effect=echo_placeholders)
    client.post("/api/dns/analyze", json={"target": "corp.example.com"})

    prompt = outgoing_prompt(route)
    for value in DNS_REAL_VALUES:
        assert value in prompt, value
    assert "placeholders" not in prompt


# --- Redactor ---

def test_placeholders_are_consistent():
    r = Redactor()
    assert r.value("example.com") == "HOST_1"
    assert r.value("EXAMPLE.com.") == "HOST_1"
    assert r.value("10.0.0.5") == "IP_1"
    assert r.value("2606:4700::1") == "IP_2"
    assert r.value("ns1.example.com") == "HOST_2"
    assert r.value("") == ""


@pytest.mark.parametrize("text,expected", [
    ("Domain: example.com.", "Domain: HOST_1."),
    ("EXAMPLE.COM", "HOST_1"),
    ("mail.example.com", "mail.HOST_1"),
    ("notexample.com", "notexample.com"),
    ("my-example.com", "my-example.com"),
    ("example.community", "example.community"),
    ("10.0.0.5", "IP_1"),
    ("(10.0.0.5)", "(IP_1)"),
    ("110.0.0.5", "110.0.0.5"),
    ("10.0.0.55", "10.0.0.55"),
    ("2606:4700::1", "IP_2"),
    ("2606:4700::10", "2606:4700::10"),
])
def test_text_boundaries(text, expected):
    r = Redactor()
    for value in ["example.com", "10.0.0.5", "2606:4700::1"]:
        r.value(value)
    assert r.text(text) == expected


def test_longer_values_replaced_first():
    r = Redactor()
    r.value("example.com")
    r.value("mail.example.com")
    assert r.text("mail.example.com and example.com") == "HOST_2 and HOST_1"


def test_restore():
    r = Redactor()
    r.value("example.com")
    r.value("10.0.0.5")
    assert r.restore("HOST_1 at IP_1, host_1 again, HOST_10 unknown") == \
        "example.com at 10.0.0.5, example.com again, HOST_10 unknown"
