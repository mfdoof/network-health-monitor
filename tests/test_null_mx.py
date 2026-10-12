import dns.name
import pytest

from api import dns_lookup
from api.analyzer import build_dns_prompt
from api.dns_lookup import NULL_MX_LABEL, run_dns_lookup
from api.redact import Redactor, redact_dns


class FakeRRset:
    def __init__(self, ttl):
        self.ttl = ttl


class FakeAnswer(list):
    def __init__(self, records, ttl=300):
        super().__init__(records)
        self.rrset = FakeRRset(ttl)


class MX:
    def __init__(self, exchange: str, preference: int):
        self.exchange = dns.name.from_text(exchange)
        self.preference = preference


class A:
    def __init__(self, address: str):
        self.address = address


class NS:
    def __init__(self, target: str):
        self.target = dns.name.from_text(target)


@pytest.fixture
def fake_resolver(monkeypatch):
    def setup(mx: list[MX]):
        answers = {
            "A": FakeAnswer([A("93.184.216.34")]),
            "AAAA": None,
            "MX": FakeAnswer(mx) if mx else None,
            "NS": FakeAnswer([NS("ns1.example.net.")]),
        }
        monkeypatch.setattr(dns_lookup, "_query", lambda target, rtype: answers[rtype])
    return setup


def test_null_mx_is_labelled(fake_resolver):
    fake_resolver([MX(".", 0)])
    result = run_dns_lookup("nomail.example.org")
    assert result["mx_records"] == [{"host": NULL_MX_LABEL, "preference": 0, "ttl": 300, "null_mx": True}]
    assert NULL_MX_LABEL == "no mail (null MX)"


def test_normal_mx_unchanged(fake_resolver):
    fake_resolver([MX("mail.example.org.", 10)])
    result = run_dns_lookup("example.org")
    assert result["mx_records"] == [{"host": "mail.example.org", "preference": 10, "ttl": 300}]


def test_null_mx_in_prompt(fake_resolver):
    fake_resolver([MX(".", 0)])
    prompt = build_dns_prompt(run_dns_lookup("nomail.example.org"))
    assert "MX records (mail servers): no mail (null MX)\n" in prompt
    assert "priority 0" not in prompt


def test_null_mx_survives_redaction(fake_resolver):
    fake_resolver([MX(".", 0)])
    redacted = redact_dns(Redactor(), run_dns_lookup("nomail.example.org"))
    assert redacted["mx_records"][0]["host"] == NULL_MX_LABEL
    assert redacted["target"] == "HOST_1"


def test_null_mx_through_the_api(client, fake_resolver):
    fake_resolver([MX(".", 0)])
    r = client.get("/api/dns/lookup?target=nomail.example.org")
    assert r.status_code == 200
    assert r.json()["mx_records"][0]["host"] == "no mail (null MX)"
