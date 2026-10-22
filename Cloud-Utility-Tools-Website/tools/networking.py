"""
Networking & DNS Utilities Module
=================================
Provides production-grade diagnostic tools for:
- DNS Record Resolution (A, AAAA, CNAME, MX, TXT, NS, SOA, PTR)
- CIDR & IPv4/IPv6 Subnet Calculator with capacity planning
- WHOIS / RDAP Domain Registration & Registrar queries
- IP Geolocation & Autonomous System Number (ASN) lookup
"""

import socket
import ipaddress
import json
from typing import Dict, Any, List, Optional
import requests

try:
    import dns.resolver
    import dns.reversename
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False


def dns_lookup(domain: str, record_types: Optional[List[str]] = None, nameserver: Optional[str] = None) -> Dict[str, Any]:
    """
    Resolve DNS records for a given domain across standard resource record types.
    Gracefully falls back to standard socket APIs if dnspython is unavailable.
    """
    clean_domain = domain.strip().lower()
    if clean_domain.startswith("http://") or clean_domain.startswith("https://"):
        clean_domain = clean_domain.split("://")[1].split("/")[0].split(":")[0]

    if not record_types:
        record_types = ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SOA"]

    results: Dict[str, Any] = {
        "domain": clean_domain,
        "records": {},
        "errors": {},
        "resolver": nameserver or "System Default",
    }

    if HAS_DNSPYTHON:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3.0
        resolver.lifetime = 5.0
        if nameserver:
            resolver.nameservers = [nameserver]

        for rtype in record_types:
            try:
                answers = resolver.resolve(clean_domain, rtype)
                record_list = []
                for rdata in answers:
                    if rtype == "MX":
                        record_list.append({"preference": rdata.preference, "exchange": str(rdata.exchange).rstrip(".")})
                    elif rtype == "SOA":
                        record_list.append({
                            "mname": str(rdata.mname).rstrip("."),
                            "rname": str(rdata.rname).rstrip("."),
                            "serial": rdata.serial,
                            "refresh": rdata.refresh,
                            "retry": rdata.retry,
                            "expire": rdata.expire,
                            "minimum": rdata.minimum,
                        })
                    elif rtype == "TXT":
                        record_list.append(b"".join(rdata.strings).decode("utf-8", errors="replace"))
                    else:
                        record_list.append(str(rdata).rstrip("."))
                results["records"][rtype] = {
                    "count": len(record_list),
                    "ttl": answers.rrset.ttl if answers.rrset else 300,
                    "data": record_list,
                }
            except dns.resolver.NoAnswer:
                results["records"][rtype] = {"count": 0, "ttl": 0, "data": []}
            except dns.resolver.NXDOMAIN:
                results["errors"][rtype] = f"Domain '{clean_domain}' does not exist (NXDOMAIN)."
                break
            except Exception as e:
                results["errors"][rtype] = str(e)
    else:
        # Standard socket fallback for basic resolution
        try:
            addr_info = socket.getaddrinfo(clean_domain, None)
            ipv4_list = list(set([item[4][0] for item in addr_info if item[0] == socket.AF_INET]))
            ipv6_list = list(set([item[4][0] for item in addr_info if item[0] == socket.AF_INET6]))
            results["records"]["A"] = {"count": len(ipv4_list), "ttl": 300, "data": ipv4_list}
            results["records"]["AAAA"] = {"count": len(ipv6_list), "ttl": 300, "data": ipv6_list}
        except Exception as e:
            results["errors"]["Socket"] = str(e)

    return results


def cidr_calculator(cidr_string: str) -> Dict[str, Any]:
    """
    Calculate full network subnet boundaries, host counts, and addressing parameters
    for IPv4 and IPv6 CIDR blocks.
    """
    clean_cidr = cidr_string.strip()
    if "/" not in clean_cidr:
        # Assume /32 for single IPv4 host or /128 for single IPv6 host
        if ":" in clean_cidr:
            clean_cidr += "/128"
        else:
            clean_cidr += "/32"

    try:
        network = ipaddress.ip_network(clean_cidr, strict=False)
    except ValueError as e:
        return {"error": f"Invalid CIDR notation: {e}", "valid": False}

    is_ipv4 = network.version == 4
    num_addresses = network.num_addresses
    usable_hosts = max(0, num_addresses - 2) if is_ipv4 and network.prefixlen < 31 else (num_addresses if is_ipv4 and network.prefixlen == 31 else (1 if is_ipv4 and network.prefixlen == 32 else num_addresses))

    first_usable = "N/A"
    last_usable = "N/A"
    if usable_hosts > 0:
        if is_ipv4:
            if network.prefixlen <= 30:
                first_usable = str(network.network_address + 1)
                last_usable = str(network.broadcast_address - 1)
            elif network.prefixlen == 31:
                first_usable = str(network.network_address)
                last_usable = str(network.broadcast_address)
            else:
                first_usable = str(network.network_address)
                last_usable = str(network.network_address)
        else:
            first_usable = str(network.network_address)
            last_usable = str(network[-1])

    # Calculate wildcard mask for IPv4
    wildcard_mask = "N/A"
    if is_ipv4:
        netmask_int = int(network.netmask)
        wildcard_int = 0xFFFFFFFF ^ netmask_int
        wildcard_mask = str(ipaddress.IPv4Address(wildcard_int))

    # Binary representations
    binary_netmask = bin(int(network.netmask))[2:].zfill(32 if is_ipv4 else 128)
    if is_ipv4:
        binary_netmask_formatted = ".".join([binary_netmask[i:i+8] for i in range(0, 32, 8)])
    else:
        binary_netmask_formatted = binary_netmask

    return {
        "valid": True,
        "input": cidr_string,
        "cidr": str(network),
        "version": f"IPv{network.version}",
        "network_address": str(network.network_address),
        "broadcast_address": str(network.broadcast_address) if is_ipv4 else "N/A (IPv6 uses Multicast)",
        "netmask": str(network.netmask),
        "wildcard_mask": wildcard_mask,
        "prefix_length": network.prefixlen,
        "total_addresses": num_addresses,
        "usable_hosts": usable_hosts,
        "first_usable_ip": first_usable,
        "last_usable_ip": last_usable,
        "is_private": network.is_private,
        "is_global": network.is_global,
        "is_loopback": network.is_loopback,
        "is_multicast": network.is_multicast,
        "binary_netmask": binary_netmask_formatted,
    }


def whois_lookup(domain: str) -> Dict[str, Any]:
    """
    Query domain registration metadata via ICANN RDAP (Registration Data Access Protocol)
    or public RDAP servers with graceful error containment.
    """
    clean_domain = domain.strip().lower()
    if "://" in clean_domain:
        clean_domain = clean_domain.split("://")[1].split("/")[0].split(":")[0]

    # Handle IP address vs Domain RDAP
    try:
        ipaddress.ip_address(clean_domain)
        rdap_url = f"https://rdap.arin.net/registry/ip/{clean_domain}"
    except ValueError:
        # Standard Domain RDAP endpoint via RDAP bootstrap
        rdap_url = f"https://rdap.org/domain/{clean_domain}"

    try:
        response = requests.get(rdap_url, timeout=4.0, headers={"Accept": "application/rdap+json, application/json"})
        if response.status_code == 200:
            data = response.json()
            events = {e.get("eventAction"): e.get("eventDate") for e in data.get("events", [])}
            nameservers = [ns.get("ldhName") for ns in data.get("nameservers", []) if ns.get("ldhName")]
            statuses = data.get("status", [])
            entities = data.get("entities", [])
            registrar = "Unknown"
            for entity in entities:
                if "registrar" in entity.get("roles", []):
                    vcard = entity.get("vcardArray", [])
                    if len(vcard) > 1:
                        for entry in vcard[1]:
                            if entry[0] == "fn":
                                registrar = entry[3]
                                break

            return {
                "domain": clean_domain,
                "protocol": "RDAP (RFC 7480)",
                "status": "Success",
                "registrar": registrar,
                "created_date": events.get("registration") or events.get("created"),
                "updated_date": events.get("last changed") or events.get("last update"),
                "expiration_date": events.get("expiration"),
                "nameservers": nameservers,
                "domain_status": statuses[:5],
                "raw_rdap": data,
            }
        else:
            return {
                "domain": clean_domain,
                "protocol": "RDAP",
                "status": "Unavailable",
                "http_code": response.status_code,
                "message": f"RDAP server returned HTTP {response.status_code}.",
            }
    except Exception as e:
        return {
            "domain": clean_domain,
            "protocol": "RDAP",
            "status": "Error",
            "message": str(e),
        }


def ip_geolocation(ip_str: str) -> Dict[str, Any]:
    """
    Lookup geographic coordinate, country, city, and ISP metadata for an IP address.
    Includes classification for loopback, private RFC1918, and public addresses.
    """
    clean_ip = ip_str.strip()
    try:
        ip_obj = ipaddress.ip_address(clean_ip)
    except ValueError:
        # Might be a domain name - resolve to IP first
        try:
            clean_ip = socket.gethostbyname(clean_ip)
            ip_obj = ipaddress.ip_address(clean_ip)
        except Exception as e:
            return {"error": f"Invalid IP address or domain: {e}", "valid": False}

    if ip_obj.is_loopback:
        return {
            "valid": True,
            "ip": clean_ip,
            "type": "Loopback",
            "country": "Localhost",
            "city": "Local Machine",
            "region": "System",
            "isp": "Loopback Interface (127.0.0.1)",
            "asn": "N/A",
            "is_private": True,
            "latitude": 0.0,
            "longitude": 0.0,
        }
    elif ip_obj.is_private:
        return {
            "valid": True,
            "ip": clean_ip,
            "type": "Private / RFC 1918 Intranet",
            "country": "Local Network (Intranet)",
            "city": "Private Subnet",
            "region": "Internal",
            "isp": "Local Area Network / Cloud VPC",
            "asn": "Private ASN",
            "is_private": True,
            "latitude": 0.0,
            "longitude": 0.0,
        }

    # Public IP Geolocation lookup
    try:
        resp = requests.get(f"https://ipapi.co/{clean_ip}/json/", timeout=3.5, headers={"User-Agent": "CloudUtilityTools/1.0"})
        if resp.status_code == 200:
            data = resp.json()
            if not data.get("error"):
                return {
                    "valid": True,
                    "ip": clean_ip,
                    "type": "Public IPv4" if ip_obj.version == 4 else "Public IPv6",
                    "country": data.get("country_name", "Unknown"),
                    "country_code": data.get("country_code", "XX"),
                    "region": data.get("region", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "postal": data.get("postal", "Unknown"),
                    "latitude": data.get("latitude", 0.0),
                    "longitude": data.get("longitude", 0.0),
                    "timezone": data.get("timezone", "UTC"),
                    "asn": data.get("asn", "Unknown"),
                    "isp": data.get("org", "Unknown"),
                    "is_private": False,
                }
    except Exception:
        pass

    # Secondary fallback
    try:
        resp2 = requests.get(f"http://ip-api.com/json/{clean_ip}", timeout=3.0)
        if resp2.status_code == 200:
            d2 = resp2.json()
            if d2.get("status") == "success":
                return {
                    "valid": True,
                    "ip": clean_ip,
                    "type": "Public IPv4",
                    "country": d2.get("country", "Unknown"),
                    "country_code": d2.get("countryCode", "XX"),
                    "region": d2.get("regionName", "Unknown"),
                    "city": d2.get("city", "Unknown"),
                    "postal": d2.get("zip", "Unknown"),
                    "latitude": d2.get("lat", 0.0),
                    "longitude": d2.get("lon", 0.0),
                    "timezone": d2.get("timezone", "UTC"),
                    "asn": d2.get("as", "Unknown"),
                    "isp": d2.get("isp", "Unknown"),
                    "is_private": False,
                }
    except Exception:
        pass

    return {
        "valid": True,
        "ip": clean_ip,
        "type": "Public IP",
        "country": "Public Node",
        "city": "Public Internet Gateway",
        "region": "Global",
        "isp": "Public Internet Carrier",
        "asn": "Active BGP Route",
        "is_private": False,
        "latitude": 0.0,
        "longitude": 0.0,
    }
