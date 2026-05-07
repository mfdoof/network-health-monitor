"""
dns_lookup.py
-------------
Performs DNS lookups for a given target (hostname or IP address).

- Hostname input: queries A, AAAA, MX, NS records (with per-record TTL)
- IP input: performs PTR reverse lookup
- Returns a structured dict consumed by the /hosts/{id}/dns route in main.py
"""

import ipaddress
import logging
from typing import Any

import dns.exception
import dns.rdatatype
import dns.resolver
import dns.reversename

logger = logging.getLogger(__name__)

# Shared resolver — raise lifetime so slow upstreams don't instantly fail
_resolver = dns.resolver.Resolver()
_resolver.lifetime = 5.0  # seconds total per query


def _is_ip(target: str) -> bool:
    """Return True if target is a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        return False


def _query(target: str, record_type: str) -> dns.resolver.Answer | None:
    """
    Run a single DNS query. Returns the Answer or None on any failure.
    Logs the specific failure reason for debugging.
    """
    try:
        return _resolver.resolve(target, record_type)
    except dns.resolver.NXDOMAIN:
        logger.warning("DNS NXDOMAIN: %s has no %s record", target, record_type)
    except dns.resolver.NoAnswer:
        logger.debug("DNS NoAnswer: %s returned no %s records", target, record_type)
    except dns.resolver.Timeout:
        logger.warning("DNS timeout querying %s for %s", record_type, target)
    except dns.exception.DNSException as exc:
        logger.error("DNS error querying %s for %s: %s", record_type, target, exc)
    return None


def _lookup_hostname(target: str) -> dict[str, Any]:
    """
    Query A, AAAA, MX, and NS records for a hostname.
    Each record carries its own TTL.
    """
    result: dict[str, Any] = {
        "lookup_type": "forward",
        "target": target,
        "a_records": [],
        "aaaa_records": [],
        "mx_records": [],
        "ns_records": [],
        "errors": [],
    }

    # --- A records ---
    answer = _query(target, "A")
    if answer:
        for rdata in answer:
            result["a_records"].append({
                "address": rdata.address,
                "ttl": answer.rrset.ttl,
            })
    else:
        result["errors"].append("No A records found")

    # --- AAAA records ---
    answer = _query(target, "AAAA")
    if answer:
        for rdata in answer:
            result["aaaa_records"].append({
                "address": rdata.address,
                "ttl": answer.rrset.ttl,
            })
    # AAAA absence is not an error — many hosts are IPv4-only

    # --- MX records ---
    answer = _query(target, "MX")
    if answer:
        for rdata in answer:
            result["mx_records"].append({
                "host": str(rdata.exchange).rstrip("."),
                "preference": rdata.preference,
                "ttl": answer.rrset.ttl,
            })
    # MX absence is not an error — not all hosts handle mail

    # --- NS records ---
    answer = _query(target, "NS")
    if answer:
        for rdata in answer:
            result["ns_records"].append({
                "nameserver": str(rdata.target).rstrip("."),
                "ttl": answer.rrset.ttl,
            })
    else:
        result["errors"].append("No NS records found")

    return result


def _lookup_ip(target: str) -> dict[str, Any]:
    """
    Perform a PTR reverse DNS lookup for an IP address.
    A, AAAA, MX, NS queries are meaningless for raw IPs.
    """
    result: dict[str, Any] = {
        "lookup_type": "reverse",
        "target": target,
        "ptr_records": [],
        "errors": [],
    }

    try:
        reverse_name = dns.reversename.from_address(target)
    except dns.exception.DNSException as exc:
        result["errors"].append(f"Could not build reverse lookup name: {exc}")
        return result

    answer = _query(str(reverse_name), "PTR")
    if answer:
        for rdata in answer:
            result["ptr_records"].append({
                "hostname": str(rdata.target).rstrip("."),
                "ttl": answer.rrset.ttl,
            })
    else:
        result["errors"].append("No PTR record found — IP may not have reverse DNS configured")

    return result


def run_dns_lookup(target: str) -> dict[str, Any]:
    """
    Entry point called by the FastAPI route.

    Args:
        target: hostname (e.g. "example.com") or IP address (e.g. "93.184.216.34")

    Returns:
        Structured dict with lookup results and any non-fatal errors.
    """
    target = target.strip()

    if not target:
        return {
            "lookup_type": None,
            "target": target,
            "errors": ["Target is empty"],
        }

    if _is_ip(target):
        logger.info("DNS lookup: IP detected, running reverse lookup for %s", target)
        return _lookup_ip(target)
    else:
        logger.info("DNS lookup: hostname detected, running forward lookup for %s", target)
        return _lookup_hostname(target)