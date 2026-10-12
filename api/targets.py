import ipaddress
import socket

from api.config import ALLOW_PRIVATE_TARGETS
from api.logger import logger

IPAddress = ipaddress.IPv4Address | ipaddress.IPv6Address

CGNAT = ipaddress.ip_network("100.64.0.0/10")


class TargetError(ValueError):
    """Base error for a target that can't be used."""


class TargetUnresolvable(TargetError):
    pass


class TargetNotAllowed(TargetError):
    pass


def resolve(host: str) -> list[IPAddress]:
    """Resolve a hostname or IP literal to all of its IPv4 and IPv6 addresses."""
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError) as e:
        raise TargetUnresolvable("Could not resolve host") from e

    addresses: list[IPAddress] = []
    for info in infos:
        # Drop any IPv6 zone id ("fe80::1%en0")
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if ip not in addresses:
            addresses.append(ip)

    if not addresses:
        raise TargetUnresolvable("Could not resolve host")
    return addresses


def is_blocked_ip(ip: IPAddress) -> bool:
    """True if the address is in a non-public range."""
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped

    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or (isinstance(ip, ipaddress.IPv4Address) and ip in CGNAT)
        or (isinstance(ip, ipaddress.IPv6Address) and ip.is_site_local)
    )


def check_target(host: str) -> str:
    """
    Resolve a host and make sure every address is allowed.
    Returns the IP to connect to, so callers never resolve the name again.
    """
    addresses = resolve(host)

    if not ALLOW_PRIVATE_TARGETS:
        blocked = [ip for ip in addresses if is_blocked_ip(ip)]
        if blocked:
            logger.warning(f"Blocked target: {host} -> {[str(ip) for ip in blocked]}")
            raise TargetNotAllowed("This host is not allowed")

    return str(addresses[0])
