"""
System Diagnostics Utilities Module
===================================
Provides web and cloud infrastructure diagnostics:
- HTTP Response Header Inspector & Security Header Posture Grader
- SSL / TLS Certificate Validity, Expiry & SANs Inspector
- UUID & Unique Identifier Generator (UUIDv1, UUIDv4, UUIDv5, bulk generator)
"""

import ssl
import socket
import uuid
import time
import requests
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


def inspect_http_headers(url: str, follow_redirects: bool = True, timeout: float = 6.0) -> Dict[str, Any]:
    """
    Perform an HTTP HEAD/GET probe to inspect response headers, measure response latency,
    and grade security header compliance (HSTS, CSP, X-Frame-Options, etc.).
    """
    clean_url = url.strip()
    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = "https://" + clean_url

    start_time = time.perf_counter()
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CloudUtilityTools/1.0; +https://github.com/rithikesh18-rk/cloud-computing)"})
        # Try HEAD first for fast diagnostics, fallback to GET
        try:
            resp = session.head(clean_url, allow_redirects=follow_redirects, timeout=timeout)
            if resp.status_code >= 400:
                resp = session.get(clean_url, allow_redirects=follow_redirects, timeout=timeout)
        except requests.RequestException:
            resp = session.get(clean_url, allow_redirects=follow_redirects, timeout=timeout)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        headers_dict = dict(resp.headers)

        # Audit security headers
        sec_checks = {
            "Strict-Transport-Security": {
                "present": "Strict-Transport-Security" in resp.headers or "strict-transport-security" in resp.headers,
                "value": resp.headers.get("Strict-Transport-Security", "Missing"),
                "recommendation": "Enforces HTTPS connections and prevents SSL-stripping attacks.",
                "weight": 25,
            },
            "Content-Security-Policy": {
                "present": "Content-Security-Policy" in resp.headers or "content-security-policy" in resp.headers,
                "value": resp.headers.get("Content-Security-Policy", "Missing"),
                "recommendation": "Restricts script execution sources to defend against Cross-Site Scripting (XSS).",
                "weight": 25,
            },
            "X-Frame-Options": {
                "present": "X-Frame-Options" in resp.headers or "x-frame-options" in resp.headers,
                "value": resp.headers.get("X-Frame-Options", "Missing"),
                "recommendation": "Defends against clickjacking by preventing iframe framing.",
                "weight": 15,
            },
            "X-Content-Type-Options": {
                "present": "X-Content-Type-Options" in resp.headers or "x-content-type-options" in resp.headers,
                "value": resp.headers.get("X-Content-Type-Options", "Missing"),
                "recommendation": "Prevents MIME-type sniffing (should be 'nosniff').",
                "weight": 15,
            },
            "Referrer-Policy": {
                "present": "Referrer-Policy" in resp.headers or "referrer-policy" in resp.headers,
                "value": resp.headers.get("Referrer-Policy", "Missing"),
                "recommendation": "Controls how much referrer information is included with requests.",
                "weight": 10,
            },
            "Permissions-Policy": {
                "present": "Permissions-Policy" in resp.headers or "permissions-policy" in resp.headers,
                "value": resp.headers.get("Permissions-Policy", "Missing"),
                "recommendation": "Restricts browser features (camera, microphone, geolocation).",
                "weight": 10,
            },
        }

        earned_points = sum(c["weight"] for c in sec_checks.values() if c["present"])
        if earned_points >= 85:
            grade = "A+"
        elif earned_points >= 70:
            grade = "A"
        elif earned_points >= 50:
            grade = "B"
        elif earned_points >= 30:
            grade = "C"
        else:
            grade = "D (Vulnerable)"

        return {
            "success": True,
            "url": clean_url,
            "status_code": resp.status_code,
            "reason": resp.reason,
            "latency_ms": latency_ms,
            "headers": headers_dict,
            "security_audit": {
                "score": earned_points,
                "grade": grade,
                "checks": sec_checks,
            },
            "redirect_history": [r.url for r in resp.history],
        }
    except Exception as e:
        return {
            "success": False,
            "url": clean_url,
            "error": str(e),
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }


def check_ssl_certificate(hostname_or_url: str, port: int = 443, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Establish a direct TLS socket connection to inspect the remote X.509 certificate,
    evaluating expiration date, remaining days, certificate authority, and SANs.
    """
    clean_host = hostname_or_url.strip()
    if clean_host.startswith("http://") or clean_host.startswith("https://"):
        parsed = urlparse(clean_host)
        clean_host = parsed.hostname or clean_host
        if parsed.port:
            port = parsed.port

    clean_host = clean_host.split(":")[0].split("/")[0]

    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((clean_host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=clean_host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()

                # Parse validity dates
                not_after_str = cert.get("notAfter")
                not_before_str = cert.get("notBefore")
                # Format: 'Sep 15 12:00:00 2027 GMT'
                exp_dt = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                start_dt = datetime.strptime(not_before_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                now_dt = datetime.now(timezone.utc)

                days_left = (exp_dt - now_dt).days
                is_valid = days_left > 0

                # Extract Issuer and Subject
                issuer_dict = dict(x[0] for x in cert.get("issuer", ()))
                subject_dict = dict(x[0] for x in cert.get("subject", ()))
                issuer_name = issuer_dict.get("organizationName") or issuer_dict.get("commonName") or "Public CA"
                common_name = subject_dict.get("commonName") or clean_host

                # Subject Alternative Names (SAN)
                sans = [item[1] for item in cert.get("subjectAltName", []) if item[0] == "DNS"]

                # Health state
                if days_left < 0:
                    health = "EXPIRED ❌"
                elif days_left < 15:
                    health = "CRITICAL (<15 days left) ⚠️"
                elif days_left < 30:
                    health = "WARNING (<30 days left) 🟡"
                else:
                    health = "HEALTHY & VALID ✅"

                return {
                    "valid": is_valid,
                    "host": clean_host,
                    "port": port,
                    "common_name": common_name,
                    "issuer": issuer_name,
                    "issuer_details": issuer_dict,
                    "valid_from": start_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "valid_until": exp_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "days_remaining": days_left,
                    "health_status": health,
                    "tls_version": version,
                    "cipher_suite": cipher[0] if cipher else "Unknown",
                    "cipher_bits": cipher[2] if cipher else 0,
                    "subject_alt_names": sans[:15],
                    "total_sans": len(sans),
                }
    except ssl.SSLCertVerificationError as e:
        return {
            "valid": False,
            "host": clean_host,
            "port": port,
            "error": f"SSL Certificate Verification Failed: {e.verify_message}",
            "health_status": "UNTRUSTED / INVALID CERTIFICATE ❌",
        }
    except Exception as e:
        return {
            "valid": False,
            "host": clean_host,
            "port": port,
            "error": str(e),
            "health_status": "CONNECTION FAILED ❌",
        }


def generate_uuids(count: int = 5, version: str = "v4", uppercase: bool = False, no_hyphens: bool = False, namespace_dns: Optional[str] = None) -> List[str]:
    """
    Generate batch unique identifiers:
    - UUIDv4 (Random CSPRNG)
    - UUIDv1 (Time-based + MAC)
    - UUIDv5 (SHA-1 Name-based)
    """
    results = []
    num = max(1, min(count, 100))

    for _ in range(num):
        if version == "v1":
            u = uuid.uuid1()
        elif version == "v5" and namespace_dns:
            u = uuid.uuid5(uuid.NAMESPACE_DNS, namespace_dns)
        else:
            u = uuid.uuid4()

        u_str = str(u)
        if no_hyphens:
            u_str = u_str.replace("-", "")
        if uppercase:
            u_str = u_str.upper()

        results.append(u_str)

    return results
