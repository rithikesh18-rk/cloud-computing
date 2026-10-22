"""
Security & Encoding Utilities Module
====================================
Provides cryptographic, decoding, and encoding primitives:
- JWT Token Inspector & Claim Validator (RFC 7519)
- Base64 & URL-Safe Encoding / Decoding (RFC 4648)
- URL Component Encoding / Decoding & Query String Parser (RFC 3986)
- Cryptographic Hashing Engine (SHA-256, SHA-512, SHA-1, MD5, HMAC-SHA256)
- High-Entropy Password & CSPRNG Secret Generator with Entropy Analysis
"""

import base64
import hashlib
import hmac
import json
import math
import secrets
import string
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, Optional

try:
    import jwt
    HAS_PYJWT = True
except ImportError:
    HAS_PYJWT = False


def decode_jwt(token: str, secret: Optional[str] = None, algorithms: Optional[list] = None) -> Dict[str, Any]:
    """
    Decode and inspect JSON Web Tokens (JWT). Parses header, claims, and payload.
    Optionally verifies cryptographic signatures using PyJWT.
    """
    clean_token = token.strip()
    if clean_token.lower().startswith("bearer "):
        clean_token = clean_token[7:].strip()

    parts = clean_token.split(".")
    if len(parts) != 3:
        return {
            "valid": False,
            "error": "Invalid JWT format. A valid token consists of three dot-separated parts: Header.Payload.Signature.",
        }

    # Manual base64url padding helper
    def b64url_decode(segment: str) -> bytes:
        rem = len(segment) % 4
        if rem > 0:
            segment += "=" * (4 - rem)
        return base64.urlsafe_b64decode(segment)

    try:
        header_bytes = b64url_decode(parts[0])
        payload_bytes = b64url_decode(parts[1])
        header = json.loads(header_bytes.decode("utf-8"))
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception as e:
        return {"valid": False, "error": f"Failed to parse JWT segments: {e}"}

    # Analyze standard claims
    now_ts = int(datetime.now(timezone.utc).timestamp())
    exp_status = "No Expiration ('exp') Claim"
    is_expired = False
    if "exp" in payload and isinstance(payload["exp"], (int, float)):
        exp_ts = int(payload["exp"])
        exp_dt = datetime.fromtimestamp(exp_ts, timezone.utc)
        if exp_ts < now_ts:
            exp_status = f"Expired ({exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}, {now_ts - exp_ts}s ago)"
            is_expired = True
        else:
            exp_status = f"Valid until {exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')} (in {exp_ts - now_ts}s)"

    issued_at = None
    if "iat" in payload and isinstance(payload["iat"], (int, float)):
        iat_dt = datetime.fromtimestamp(int(payload["iat"]), timezone.utc)
        issued_at = iat_dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    not_before = None
    if "nbf" in payload and isinstance(payload["nbf"], (int, float)):
        nbf_dt = datetime.fromtimestamp(int(payload["nbf"]), timezone.utc)
        not_before = nbf_dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Signature verification if secret provided
    signature_verification = "Unverified (No secret key provided)"
    if secret:
        if HAS_PYJWT:
            try:
                algs = algorithms or [header.get("alg", "HS256")]
                jwt.decode(clean_token, secret, algorithms=algs, options={"verify_signature": True})
                signature_verification = "Signature Verified Successfully ✅"
            except jwt.ExpiredSignatureError:
                signature_verification = "Signature Verified ✅ (Note: Token is Expired)"
            except jwt.InvalidSignatureError:
                signature_verification = "Signature Verification FAILED ❌ (Invalid Secret/Key)"
            except Exception as e:
                signature_verification = f"Verification Error: {e}"
        else:
            signature_verification = "PyJWT library required for signature validation."

    return {
        "valid": True,
        "algorithm": header.get("alg", "None"),
        "type": header.get("typ", "JWT"),
        "header": header,
        "payload": payload,
        "signature_raw": parts[2],
        "is_expired": is_expired,
        "expiration_status": exp_status,
        "issued_at": issued_at,
        "not_before": not_before,
        "subject": payload.get("sub"),
        "issuer": payload.get("iss"),
        "audience": payload.get("aud"),
        "signature_verification": signature_verification,
    }


def encode_base64(text: str, url_safe: bool = False) -> str:
    """Encode string or binary input to Base64 (Standard or URL-safe)."""
    raw_bytes = text.encode("utf-8")
    if url_safe:
        return base64.urlsafe_b64encode(raw_bytes).decode("ascii")
    return base64.b64encode(raw_bytes).decode("ascii")


def decode_base64(encoded_text: str, url_safe: bool = False) -> Dict[str, Any]:
    """Decode standard or URL-safe Base64 string with automatic padding recovery."""
    clean = encoded_text.strip()
    rem = len(clean) % 4
    if rem > 0:
        clean += "=" * (4 - rem)

    try:
        if url_safe:
            decoded_bytes = base64.urlsafe_b64decode(clean)
        else:
            decoded_bytes = base64.b64decode(clean)

        try:
            utf8_text = decoded_bytes.decode("utf-8")
            is_text = True
        except UnicodeDecodeError:
            utf8_text = None
            is_text = False

        return {
            "success": True,
            "text": utf8_text,
            "hex": decoded_bytes.hex(),
            "byte_length": len(decoded_bytes),
            "is_utf8": is_text,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def encode_url(text: str, full_component: bool = True) -> str:
    """URL encode string (RFC 3986 percent-encoding)."""
    if full_component:
        return urllib.parse.quote(text, safe="")
    return urllib.parse.quote(text)


def decode_url(encoded_text: str) -> str:
    """URL decode percent-encoded string."""
    return urllib.parse.unquote(encoded_text)


def parse_query_string(url_or_query: str) -> Dict[str, Any]:
    """Parse URL or query string into structured key-value parameters."""
    if "?" in url_or_query:
        query_part = url_or_query.split("?", 1)[1]
    else:
        query_part = url_or_query

    parsed = urllib.parse.parse_qs(query_part)
    # Simplify single-item lists
    flattened = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    return {"raw_query": query_part, "parameters": flattened}


def generate_hashes(text: str, hmac_key: Optional[str] = None) -> Dict[str, str]:
    """
    Generate standard cryptographic hashes (SHA-256, SHA-512, SHA-1, MD5)
    and optional HMAC-SHA256.
    """
    raw_bytes = text.encode("utf-8")
    results = {
        "input_length": len(text),
        "md5": hashlib.md5(raw_bytes).hexdigest(),
        "sha1": hashlib.sha1(raw_bytes).hexdigest(),
        "sha224": hashlib.sha224(raw_bytes).hexdigest(),
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "sha384": hashlib.sha384(raw_bytes).hexdigest(),
        "sha512": hashlib.sha512(raw_bytes).hexdigest(),
    }
    if hmac_key:
        key_bytes = hmac_key.encode("utf-8")
        results["hmac_sha256"] = hmac.new(key_bytes, raw_bytes, hashlib.sha256).hexdigest()
        results["hmac_sha512"] = hmac.new(key_bytes, raw_bytes, hashlib.sha512).hexdigest()

    return results


def calculate_entropy(password: str) -> Dict[str, Any]:
    """Compute Shannon and pool-based entropy bits and estimate brute-force complexity."""
    if not password:
        return {"bits": 0.0, "strength": "Empty", "crack_time": "Instant"}

    pool = 0
    if any(c in string.ascii_lowercase for c in password):
        pool += 26
    if any(c in string.ascii_uppercase for c in password):
        pool += 26
    if any(c in string.digits for c in password):
        pool += 10
    if any(c in string.punctuation for c in password):
        pool += 32
    if any(c == " " for c in password):
        pool += 1

    pool = max(pool, 1)
    bits = len(password) * math.log2(pool)

    if bits < 40:
        strength = "Very Weak"
        crack_time = "< 1 Second"
    elif bits < 60:
        strength = "Weak"
        crack_time = "Few Minutes"
    elif bits < 80:
        strength = "Moderate"
        crack_time = "Several Months"
    elif bits < 100:
        strength = "Strong"
        crack_time = "Thousands of Years"
    else:
        strength = "Very Strong"
        crack_time = "Centuries / Uncrackable"

    return {
        "bits": round(bits, 2),
        "pool_size": pool,
        "length": len(password),
        "strength": strength,
        "crack_time": crack_time,
    }


def generate_secure_password(
    length: int = 20,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False
) -> Dict[str, Any]:
    """
    Generate cryptographically secure random password using CSPRNG (secrets).
    Guarantees inclusion of selected character classes.
    """
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?"

    if exclude_ambiguous:
        ambiguous = "0O1lI|"
        upper = "".join(c for c in upper if c not in ambiguous)
        lower = "".join(c for c in lower if c not in ambiguous)
        digits = "".join(c for c in digits if c not in ambiguous)
        symbols = "".join(c for c in symbols if c not in ambiguous)

    charset = ""
    guaranteed = []

    if use_upper and upper:
        charset += upper
        guaranteed.append(secrets.choice(upper))
    if use_lower and lower:
        charset += lower
        guaranteed.append(secrets.choice(lower))
    if use_digits and digits:
        charset += digits
        guaranteed.append(secrets.choice(digits))
    if use_symbols and symbols:
        charset += symbols
        guaranteed.append(secrets.choice(symbols))

    if not charset:
        charset = string.ascii_letters + string.digits
        guaranteed.append(secrets.choice(charset))

    target_length = max(length, len(guaranteed))
    remaining = [secrets.choice(charset) for _ in range(target_length - len(guaranteed))]
    password_chars = guaranteed + remaining

    # CSPRNG Fisher-Yates shuffle
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    password = "".join(password_chars)
    entropy_info = calculate_entropy(password)

    return {
        "password": password,
        "length": len(password),
        "entropy": entropy_info,
    }
