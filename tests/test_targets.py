import ipaddress

import pytest

from api import targets
from api.targets import TargetNotAllowed, TargetUnresolvable, check_target, is_blocked_ip
from tests.conftest import add_host

BLOCKED = {
    "private 10/8": "10.0.0.5",
    "private 172.16/12": "172.16.0.1",
    "private 192.168/16": "192.168.1.1",
    "loopback v4": "127.0.0.1",
    "loopback v6": "::1",
    "link-local v4": "169.254.10.1",
    "cloud metadata": "169.254.169.254",
    "link-local v6": "fe80::1",
    "CGNAT": "100.64.0.1",
    "CGNAT upper": "100.127.255.254",
    "multicast v4": "224.0.0.1",
    "multicast v6": "ff02::1",
    "reserved": "240.0.0.1",
    "unspecified v4": "0.0.0.0",
    "unspecified v6": "::",
    "unique local v6": "fd00::1",
    "site-local v6": "fec0::1",
    "v4-mapped loopback": "::ffff:127.0.0.1",
    "v4-mapped private": "::ffff:10.0.0.1",
}

PUBLIC = ["45.33.32.156", "8.8.8.8", "2600:3c01::f03c:91ff:fe18:bb2f"]


@pytest.mark.parametrize("ip", BLOCKED.values(), ids=BLOCKED.keys())
def test_blocked_ranges(ip, fake_dns):
    assert is_blocked_ip(ipaddress.ip_address(ip))
    fake_dns({"target.test": [ip]})
    with pytest.raises(TargetNotAllowed):
        check_target("target.test")


@pytest.mark.parametrize("ip", PUBLIC)
def test_public_addresses_allowed(ip, fake_dns):
    assert not is_blocked_ip(ipaddress.ip_address(ip))
    fake_dns({"target.test": [ip]})
    assert check_target("target.test") == ip


def test_any_private_address_blocks_the_host(fake_dns):
    fake_dns({"mixed.test": ["45.33.32.156", "2600:3c01::1", "10.0.0.5"]})
    with pytest.raises(TargetNotAllowed):
        check_target("mixed.test")


def test_private_v6_among_public_v4_blocks(fake_dns):
    fake_dns({"mixed.test": ["45.33.32.156", "::1"]})
    with pytest.raises(TargetNotAllowed):
        check_target("mixed.test")


def test_allow_private_targets_setting(fake_dns, monkeypatch):
    monkeypatch.setattr(targets, "ALLOW_PRIVATE_TARGETS", True)
    fake_dns({"lan.test": ["192.168.1.10"]})
    assert check_target("lan.test") == "192.168.1.10"


def test_unresolvable_host(fake_dns):
    fake_dns({})
    with pytest.raises(TargetUnresolvable):
        check_target("nope.test")


def test_ipv6_zone_id_is_stripped(fake_dns):
    fake_dns({"zoned.test": ["fe80::1%en0"]})
    with pytest.raises(TargetNotAllowed):
        check_target("zoned.test")


# --- Routes ---

@pytest.mark.parametrize("host,ips", [
    ("10.0.0.5", ["10.0.0.5"]),
    ("::1", ["::1"]),
    ("evil.example.com", ["192.168.1.10"]),
])
def test_add_blocked_host_returns_403(client, fake_dns, host, ips):
    fake_dns({host: ips})
    r = client.post("/api/hosts", json={"host": host})
    assert r.status_code == 403
    assert r.json() == {"detail": "This host is not allowed"}


def test_localhost_is_rejected(client, fake_dns):
    fake_dns({"localhost": ["127.0.0.1"]})
    assert client.post("/api/hosts", json={"host": "localhost"}).status_code in (403, 422)


def test_unresolvable_host_returns_400(client, fake_dns):
    fake_dns({})
    assert client.post("/api/hosts", json={"host": "nope.example.com"}).status_code == 400


def test_scan_and_ping_use_the_checked_ip(client, fake_dns, connections, ping_calls):
    fake_dns({"scanme.example.com": ["45.33.32.156"]})
    host_id = add_host(client, "scanme.example.com")

    r = client.post(f"/api/hosts/{host_id}/scan", json={"ports": [22, 80]})
    assert r.status_code == 200
    assert r.json()["open_ports"] == [22]
    assert connections and {h for h, _ in connections} == {"45.33.32.156"}

    r = client.get(f"/api/hosts/{host_id}/ping")
    assert r.status_code == 200
    assert ping_calls[0][-1] == "45.33.32.156"
    assert "scanme.example.com" not in ping_calls[0]
    assert r.json()["latency_ms"] == 153.402


def test_dns_rebinding_blocked_at_scan_and_ping_time(client, fake_dns, connections, ping_calls):
    fake_dns({"rebind.example.com": ["45.33.32.156"]})
    host_id = add_host(client, "rebind.example.com")

    # The name now points at a private address
    fake_dns({"rebind.example.com": ["10.0.0.5"]})

    assert client.post(f"/api/hosts/{host_id}/scan", json={"ports": [22]}).status_code == 403
    assert client.get(f"/api/hosts/{host_id}/ping").status_code == 403
    assert connections == []
    assert ping_calls == []
