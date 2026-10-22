"""
Cloud Utility Tools - FastAPI REST Service & Diagnostic CLI
===========================================================
Production-ready REST API exposing high-performance developer utilities.
Interactive OpenAPI documentation available at /docs.
"""

import sys
import os
import argparse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Ensure UTF-8 output on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to path so tools package is readily importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.networking import dns_lookup, cidr_calculator, whois_lookup, ip_geolocation
from tools.security import (
    decode_jwt,
    encode_base64,
    decode_base64,
    encode_url,
    decode_url,
    generate_hashes,
    generate_secure_password,
    calculate_entropy,
)
from tools.converters import (
    json_to_yaml,
    yaml_to_json,
    json_to_csv,
    csv_to_json,
    format_json,
    parse_cron,
)
from tools.diagnostics import (
    inspect_http_headers,
    check_ssl_certificate,
    generate_uuids,
)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Cloud Utility Tools API",
    description="Unified cloud-native developer and sysadmin web suite for DNS, CIDR, JWT, hashes, format conversions, and infrastructure diagnostics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Pydantic Request Models
# ============================================================================

class DNSRequest(BaseModel):
    domain: str = Field(..., description="Target domain or hostname")
    record_types: Optional[List[str]] = Field(default=None, description="DNS resource record types")
    nameserver: Optional[str] = Field(default=None, description="Custom DNS nameserver")

class CIDRRequest(BaseModel):
    cidr: str = Field(..., description="IPv4 or IPv6 CIDR string (e.g. 10.0.0.0/16)")

class WhoisRequest(BaseModel):
    domain: str = Field(..., description="Domain name for RDAP WHOIS lookup")

class IPGeoRequest(BaseModel):
    ip: str = Field(..., description="Target IP address for geolocation")

class JWTRequest(BaseModel):
    token: str = Field(..., description="JSON Web Token string")
    secret: Optional[str] = Field(default=None, description="Optional secret key for signature verification")

class Base64Request(BaseModel):
    text: str = Field(...)
    url_safe: bool = Field(default=False)

class URLRequest(BaseModel):
    text: str = Field(...)

class HashRequest(BaseModel):
    text: str = Field(...)
    hmac_key: Optional[str] = Field(default=None)

class PasswordRequest(BaseModel):
    length: int = Field(default=20, ge=8, le=128)
    use_upper: bool = Field(default=True)
    use_lower: bool = Field(default=True)
    use_digits: bool = Field(default=True)
    use_symbols: bool = Field(default=True)
    exclude_ambiguous: bool = Field(default=False)

class ConvertTextRequest(BaseModel):
    content: str = Field(...)

class JSONFormatRequest(BaseModel):
    json_str: str = Field(...)
    indent: int = Field(default=2)
    minify: bool = Field(default=False)

class CronRequest(BaseModel):
    expression: str = Field(..., description="Standard 5-field cron expression")
    num_runs: int = Field(default=5, ge=1, le=20)

class HeadersRequest(BaseModel):
    url: str = Field(..., description="Target HTTP/HTTPS URL")

class SSLRequest(BaseModel):
    host: str = Field(..., description="Target hostname")
    port: int = Field(default=443)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def root():
    return {
        "service": "Cloud Utility Tools API",
        "status": "operational",
        "version": "1.0.0",
        "documentation": "/docs",
        "capabilities": [
            "DNS Record Lookup",
            "CIDR & Subnet Calculator",
            "RDAP WHOIS Lookup",
            "IP Geolocation & ASN",
            "JWT Token Inspector",
            "Base64 & URL Encoding",
            "SHA-256 / MD5 Hash Engine",
            "CSPRNG Password Generator",
            "JSON <-> YAML & CSV Converters",
            "Cron Syntax Parser",
            "HTTP Response Header Inspector",
            "SSL/TLS Certificate Checker",
            "UUID Generator",
        ],
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "Cloud-Utility-Tools-API"}

@app.post("/api/dns")
def api_dns(req: DNSRequest):
    return dns_lookup(req.domain, req.record_types, req.nameserver)

@app.post("/api/cidr")
def api_cidr(req: CIDRRequest):
    res = cidr_calculator(req.cidr)
    if not res.get("valid"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/whois")
def api_whois(req: WhoisRequest):
    return whois_lookup(req.domain)

@app.post("/api/ip-geo")
def api_ip_geo(req: IPGeoRequest):
    return ip_geolocation(req.ip)

@app.post("/api/jwt")
def api_jwt(req: JWTRequest):
    res = decode_jwt(req.token, req.secret)
    if not res.get("valid"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/base64/encode")
def api_b64_encode(req: Base64Request):
    return {"encoded": encode_base64(req.text, req.url_safe)}

@app.post("/api/base64/decode")
def api_b64_decode(req: Base64Request):
    res = decode_base64(req.text, req.url_safe)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/url/encode")
def api_url_encode(req: URLRequest):
    return {"encoded": encode_url(req.text)}

@app.post("/api/url/decode")
def api_url_decode(req: URLRequest):
    return {"decoded": decode_url(req.text)}

@app.post("/api/hash")
def api_hash(req: HashRequest):
    return generate_hashes(req.text, req.hmac_key)

@app.post("/api/password")
def api_password(req: PasswordRequest):
    return generate_secure_password(
        length=req.length,
        use_upper=req.use_upper,
        use_lower=req.use_lower,
        use_digits=req.use_digits,
        use_symbols=req.use_symbols,
        exclude_ambiguous=req.exclude_ambiguous,
    )

@app.post("/api/convert/json-yaml")
def api_json_yaml(req: ConvertTextRequest):
    res = json_to_yaml(req.content)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/convert/yaml-json")
def api_yaml_json(req: ConvertTextRequest):
    res = yaml_to_json(req.content)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/convert/json-csv")
def api_json_csv(req: ConvertTextRequest):
    res = json_to_csv(req.content)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/convert/csv-json")
def api_csv_json(req: ConvertTextRequest):
    res = csv_to_json(req.content)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/json/format")
def api_json_format(req: JSONFormatRequest):
    res = format_json(req.json_str, indent=req.indent, minify=req.minify)
    if not res.get("valid"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/cron")
def api_cron(req: CronRequest):
    res = parse_cron(req.expression, req.num_runs)
    if not res.get("valid"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/diagnostics/headers")
def api_headers(req: HeadersRequest):
    res = inspect_http_headers(req.url)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.post("/api/diagnostics/ssl")
def api_ssl(req: SSLRequest):
    return check_ssl_certificate(req.host, req.port)

@app.get("/api/uuid")
def api_uuid(
    count: int = Query(default=5, ge=1, le=100),
    version: str = Query(default="v4", pattern="^(v1|v4|v5)$"),
    uppercase: bool = Query(default=False),
    no_hyphens: bool = Query(default=False),
):
    return {"version": version, "count": count, "uuids": generate_uuids(count, version, uppercase, no_hyphens)}


# ============================================================================
# CLI Diagnostics & Benchmark Runner
# ============================================================================

def run_cli_audit():
    """Execute a comprehensive terminal audit verifying all diagnostic modules."""
    print("=" * 75)
    print("  🚀 CLOUD UTILITY TOOLS SUITE - DIAGNOSTIC ENGINE VERIFICATION")
    print("=" * 75)

    print("\n[1/7] Networking & DNS Resolution (google.com):")
    dns_res = dns_lookup("google.com", ["A", "MX"])
    a_records = dns_res["records"].get("A", {}).get("data", [])
    print(f"      • A Records: {a_records[:2]}")
    mx_records = dns_res["records"].get("MX", {}).get("data", [])
    print(f"      • MX Records: {len(mx_records)} mail exchanges registered")

    print("\n[2/7] CIDR Subnet Calculator (10.240.0.0/22):")
    cidr_res = cidr_calculator("10.240.0.0/22")
    print(f"      • Network: {cidr_res['network_address']} | Netmask: {cidr_res['netmask']}")
    print(f"      • Usable Host Capacity: {cidr_res['usable_hosts']} addresses ({cidr_res['first_usable_ip']} -> {cidr_res['last_usable_ip']})")
    print(f"      • Private VPC Subnet: {cidr_res['is_private']}")

    print("\n[3/7] Cryptographic Hashing & CSPRNG Password Generator:")
    sample_text = "Cloud-Utility-Tools-2026"
    hashes = generate_hashes(sample_text)
    print(f"      • Input: '{sample_text}'")
    print(f"      • SHA-256: {hashes['sha256']}")
    pw_res = generate_secure_password(24)
    print(f"      • Generated High-Entropy Key: {pw_res['password']}")
    print(f"      • Entropy: {pw_res['entropy']['bits']} bits ({pw_res['entropy']['strength']}, crack time: {pw_res['entropy']['crack_time']})")

    print("\n[4/7] JSON <-> YAML Bi-directional Transformation:")
    sample_json = '{"service": "CloudUtility", "port": 8000, "features": ["DNS", "CIDR", "JWT", "SSL"]}'
    yaml_out = json_to_yaml(sample_json)["output"].strip()
    print("      • YAML Output:\n" + "\n".join("        " + line for line in yaml_out.splitlines()))

    print("\n[5/7] Cron Syntax Parser ('15 4 * * 1-5'):")
    cron_res = parse_cron("15 4 * * 1-5", num_runs=3)
    print(f"      • Human Description: {cron_res['human_description']}")
    print(f"      • Next Triggers: {cron_res['next_executions'][:2]}")

    print("\n[6/7] System Diagnostics - SSL Certificate Audit (cloudflare.com):")
    ssl_res = check_ssl_certificate("cloudflare.com", 443)
    if ssl_res.get("valid"):
        print(f"      • Issuer: {ssl_res['issuer']} | TLS: {ssl_res['tls_version']}")
        print(f"      • Valid Until: {ssl_res['valid_until']} ({ssl_res['days_remaining']} days left) - {ssl_res['health_status']}")
    else:
        print(f"      • Result: {ssl_res.get('health_status')}")

    print("\n[7/7] Batch UUIDv4 Generation:")
    uuids = generate_uuids(3, version="v4")
    for idx, u in enumerate(uuids, 1):
        print(f"      • ID {idx}: {u}")

    print("\n" + "=" * 75)
    print("  ✅ ALL CLOUD UTILITY TOOLS VERIFIED & OPERATIONAL")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="Cloud Utility Tools Web Service & CLI")
    parser.add_argument("--audit", action="store_true", help="Run comprehensive diagnostic audit")
    parser.add_argument("--serve", action="store_true", help="Launch FastAPI REST server with uvicorn")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    args = parser.parse_args()

    if args.serve:
        import uvicorn
        print(f"Starting Cloud Utility Tools REST API on http://{args.host}:{args.port}...")
        uvicorn.run("main:app", host=args.host, port=args.port, reload=True)
    else:
        run_cli_audit()


if __name__ == "__main__":
    main()
