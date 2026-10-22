"""
Automated Pytest Suite for Cloud Utility Tools
==============================================
Validates networking, security, data conversion, and diagnostics modules,
as well as FastAPI REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from tools.networking import dns_lookup, cidr_calculator, whois_lookup, ip_geolocation
from tools.security import (
    decode_jwt,
    encode_base64,
    decode_base64,
    encode_url,
    decode_url,
    parse_query_string,
    generate_hashes,
    calculate_entropy,
    generate_secure_password,
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
from main import app

client = TestClient(app)


# ============================================================================
# Networking & DNS Tests
# ============================================================================

def test_cidr_calculator_ipv4():
    res = cidr_calculator("192.168.1.0/24")
    assert res["valid"] is True
    assert res["network_address"] == "192.168.1.0"
    assert res["broadcast_address"] == "192.168.1.255"
    assert res["netmask"] == "255.255.255.0"
    assert res["wildcard_mask"] == "0.0.0.255"
    assert res["total_addresses"] == 256
    assert res["usable_hosts"] == 254
    assert res["first_usable_ip"] == "192.168.1.1"
    assert res["last_usable_ip"] == "192.168.1.254"
    assert res["is_private"] is True


def test_cidr_calculator_invalid():
    res = cidr_calculator("999.999.999.999/24")
    assert res["valid"] is False
    assert "Invalid CIDR" in res["error"]


def test_ip_geolocation_private():
    res = ip_geolocation("10.0.0.1")
    assert res["valid"] is True
    assert res["is_private"] is True
    assert "RFC 1918" in res["type"]


def test_ip_geolocation_loopback():
    res = ip_geolocation("127.0.0.1")
    assert res["valid"] is True
    assert res["type"] == "Loopback"


def test_dns_lookup_structure():
    res = dns_lookup("google.com", ["A"])
    assert res["domain"] == "google.com"
    assert "records" in res
    assert "A" in res["records"]


# ============================================================================
# Security & Encoding Tests
# ============================================================================

def test_base64_roundtrip():
    original = "Cloud Native Sysadmin & DevOps Suite 2026! 🚀"
    encoded = encode_base64(original)
    decoded = decode_base64(encoded)
    assert decoded["success"] is True
    assert decoded["text"] == original


def test_base64_urlsafe():
    sample = "test+symbols?foo=bar/baz"
    enc = encode_base64(sample, url_safe=True)
    assert "+" not in enc
    assert "/" not in enc
    dec = decode_base64(enc, url_safe=True)
    assert dec["text"] == sample


def test_url_encode_decode():
    raw = "https://example.com/search?q=cloud utilities&lang=en#top"
    encoded = encode_url(raw)
    decoded = decode_url(encoded)
    assert decoded == raw


def test_parse_query_string():
    qs = "https://api.cloud.local/query?service=dns&debug=true&count=10"
    parsed = parse_query_string(qs)
    assert parsed["parameters"]["service"] == "dns"
    assert parsed["parameters"]["debug"] == "true"
    assert parsed["parameters"]["count"] == "10"


def test_cryptographic_hashes():
    text = "Hello Cloud Computing"
    h = generate_hashes(text, hmac_key="secret123")
    assert len(h["sha256"]) == 64
    assert len(h["sha512"]) == 128
    assert len(h["md5"]) == 32
    assert "hmac_sha256" in h
    assert len(h["hmac_sha256"]) == 64


def test_password_generator_entropy():
    p = generate_secure_password(length=24, use_upper=True, use_lower=True, use_digits=True, use_symbols=True)
    assert len(p["password"]) == 24
    assert p["entropy"]["bits"] >= 100
    assert p["entropy"]["strength"] == "Very Strong"


def test_jwt_decoder_basic():
    # Construct test JWT without signature: {"alg": "none"}.{"sub": "admin123", "name": "Cloud Admin"}
    header_b64 = encode_base64('{"alg":"none","typ":"JWT"}', url_safe=True).rstrip("=")
    payload_b64 = encode_base64('{"sub":"admin123","name":"Cloud Admin","role":"sysadmin"}', url_safe=True).rstrip("=")
    fake_token = f"{header_b64}.{payload_b64}.dummySignature"

    res = decode_jwt(fake_token)
    assert res["valid"] is True
    assert res["header"]["alg"] == "none"
    assert res["payload"]["sub"] == "admin123"
    assert res["payload"]["role"] == "sysadmin"


# ============================================================================
# Data Converters Tests
# ============================================================================

def test_json_yaml_roundtrip():
    original_json = '{"project": "CloudUtility", "version": 1, "active": true}'
    yaml_res = json_to_yaml(original_json)
    assert yaml_res["success"] is True

    json_res = yaml_to_json(yaml_res["output"])
    assert json_res["success"] is True
    assert json_res["data"]["project"] == "CloudUtility"
    assert json_res["data"]["version"] == 1


def test_json_csv_roundtrip():
    json_data = '[{"id": 1, "name": "DNS Prober"}, {"id": 2, "name": "CIDR Calc"}]'
    csv_res = json_to_csv(json_data)
    assert csv_res["success"] is True
    assert "id,name" in csv_res["output"]

    back_to_json = csv_to_json(csv_res["output"])
    assert back_to_json["success"] is True
    assert len(back_to_json["data"]) == 2


def test_format_json_minify():
    messy_json = '{\n  "service":  "CloudTools",  "status": "ok"  \n}'
    beautified = format_json(messy_json, indent=2)
    assert beautified["valid"] is True

    minified = format_json(messy_json, minify=True)
    assert minified["valid"] is True
    assert minified["output"] == '{"service":"CloudTools","status":"ok"}'


def test_parse_cron():
    res = parse_cron("0 */2 * * 1-5", num_runs=3)
    assert res["valid"] is True
    assert len(res["next_executions"]) == 3
    assert "Runs every 2 hours" in res["human_description"]


# ============================================================================
# System Diagnostics & FastAPI Tests
# ============================================================================

def test_generate_uuids():
    uuids = generate_uuids(count=5, version="v4", uppercase=False)
    assert len(uuids) == 5
    assert len(uuids[0]) == 36
    assert uuids[0].count("-") == 4


def test_fastapi_endpoints():
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["service"] == "Cloud Utility Tools API"

    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "healthy"

    r_cidr = client.post("/api/cidr", json={"cidr": "172.16.0.0/16"})
    assert r_cidr.status_code == 200
    assert r_cidr.json()["usable_hosts"] == 65534

    r_hash = client.post("/api/hash", json={"text": "IntegrationTest"})
    assert r_hash.status_code == 200
    assert len(r_hash.json()["sha256"]) == 64

    r_cron = client.post("/api/cron", json={"expression": "*/15 * * * *", "num_runs": 2})
    assert r_cron.status_code == 200
    assert r_cron.json()["valid"] is True
