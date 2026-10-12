import ipaddress
import re


class Redactor:
    """
    Swaps IPs and hostnames for stable placeholders (IP_1, HOST_1, ...) before
    data goes to the LLM, and puts the real values back in the reply.
    One instance per request so placeholders stay consistent within a prompt.
    """

    def __init__(self) -> None:
        self._to_placeholder: dict[str, str] = {}
        self._to_real: dict[str, str] = {}
        self._counts = {"IP": 0, "HOST": 0}

    def value(self, real: str) -> str:
        """Placeholder for one IP or hostname. Empty values pass through."""
        if not real:
            return real
        key = real.lower().rstrip(".")
        if key not in self._to_placeholder:
            kind = "IP" if _is_ip(key) else "HOST"
            self._counts[kind] += 1
            placeholder = f"{kind}_{self._counts[kind]}"
            self._to_placeholder[key] = placeholder
            self._to_real[placeholder] = real.rstrip(".")
        return self._to_placeholder[key]

    def text(self, text: str) -> str:
        """Replace every known real value in free text, longest first."""
        for real in sorted(self._to_placeholder, key=len, reverse=True):
            # A leading "." is allowed so subdomains like mail.<host> are covered too
            pattern = rf"(?<![\w:-]){re.escape(real)}(?![\w:-]|\.\w)"
            text = re.sub(pattern, self._to_placeholder[real], text, flags=re.IGNORECASE)
        return text

    def restore(self, text: str) -> str:
        """Put real values back for any placeholder in the reply."""
        def swap(m: re.Match) -> str:
            return self._to_real.get(m.group(0).upper(), m.group(0))
        return re.sub(r"\b(?:IP|HOST)_\d+\b", swap, text, flags=re.IGNORECASE)


def _is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def redact_scan(r: Redactor, scan_result: dict) -> dict:
    return {**scan_result, "host": r.value(scan_result["host"])}


def redact_dns(r: Redactor, dns_result: dict) -> dict:
    def records(key: str, field: str) -> list[dict]:
        # A null MX label is not a hostname, so it is left as is
        return [
            rec if rec.get("null_mx") else {**rec, field: r.value(rec[field])}
            for rec in dns_result.get(key, [])
        ]

    redacted = {
        **dns_result,
        "target": r.value(dns_result["target"]),
        "a_records": records("a_records", "address"),
        "aaaa_records": records("aaaa_records", "address"),
        "mx_records": records("mx_records", "host"),
        "ns_records": records("ns_records", "nameserver"),
        "ptr_records": records("ptr_records", "hostname"),
    }
    # Error strings can echo the target or a record
    redacted["errors"] = [r.text(e) for e in dns_result.get("errors", [])]
    return redacted
