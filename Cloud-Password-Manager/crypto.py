"""
Zero-Knowledge Cryptographic Utility Module
===========================================
Implements authenticated client-side encryption and key derivation primitives:
- Key Derivation: Argon2id (RFC 9106) and PBKDF2-HMAC-SHA256 (NIST SP 800-132)
- Symmetric Authenticated Encryption: AES-256-GCM (NIST SP 800-38D)
- Secure Randomness: CSPRNG (os.urandom, secrets)
- Constant-Time Comparison: hmac.compare_digest
- Entropy Assessment & High-Entropy Password Generation
"""

import os
import base64
import hmac
import math
import secrets
import string
from typing import Tuple, Dict, Any, Optional

# Cryptography primitives
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag

# Optional Argon2 support with graceful PBKDF2 fallback
try:
    import argon2.low_level
    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False


# ============================================================================
# Constant Definitions & Security Defaults
# ============================================================================
AES_KEY_BYTES = 32          # 256-bit encryption key
GCM_NONCE_BYTES = 12        # 96-bit recommended nonce for AES-GCM
SALT_BYTES = 16             # 128-bit salt
PBKDF2_ITERATIONS = 600000  # OWASP 2024 recommended minimum for PBKDF2-SHA256
ARGON2_TIME_COST = 3        # Argon2id iterations
ARGON2_MEMORY_COST = 65536  # Argon2id 64 MB memory cost
ARGON2_PARALLELISM = 4      # Argon2id parallel lanes


# ============================================================================
# Key Derivation Functions (KDF)
# ============================================================================

def generate_salt(num_bytes: int = SALT_BYTES) -> bytes:
    """Generate cryptographically secure random salt."""
    return os.urandom(num_bytes)


def salt_to_b64(salt: bytes) -> str:
    """Encode salt bytes to Base64 string."""
    return base64.b64encode(salt).decode("utf-8")


def b64_to_salt(b64_str: str) -> bytes:
    """Decode Base64 string back to salt bytes."""
    return base64.b64decode(b64_str.encode("utf-8"))


def derive_vault_key(
    master_password: str,
    salt: bytes,
    algorithm: str = "argon2id"
) -> bytes:
    """
    Derive a 256-bit AES encryption key from the user's master password.
    
    ZERO-KNOWLEDGE ARCHITECTURE:
    This derived key NEVER leaves the local client memory. It is used
    exclusively client-side to encrypt and decrypt credential payloads.
    """
    pw_bytes = master_password.encode("utf-8")
    
    if algorithm.lower() == "argon2id" and HAS_ARGON2:
        try:
            return argon2.low_level.hash_secret_raw(
                secret=pw_bytes,
                salt=salt,
                time_cost=ARGON2_TIME_COST,
                memory_cost=ARGON2_MEMORY_COST,
                parallelism=ARGON2_PARALLELISM,
                hash_len=AES_KEY_BYTES,
                type=argon2.low_level.Type.ID
            )
        except Exception:
            pass  # Fall through to PBKDF2 if Argon2 execution encounters issues
            
    # NIST SP 800-132 PBKDF2-HMAC-SHA256 standard
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_BYTES,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(pw_bytes)


def hash_master_auth(
    master_password: str,
    auth_salt: bytes,
    algorithm: str = "argon2id"
) -> str:
    """
    Compute the master password authentication verifier for the server/database.
    
    CRITICAL ZERO-KNOWLEDGE SEPARATION:
    The auth verifier uses an independent random salt (`auth_salt`) separate from 
    the vault encryption key salt (`kdf_salt`). 
    
    Even if the server database is completely compromised:
    1. The attacker only has the auth verifier.
    2. The attacker CANNOT derive the vault AES encryption key.
    3. The ciphertext stored in the database remains completely undecryptable.
    """
    pw_bytes = master_password.encode("utf-8")
    
    if algorithm.lower() == "argon2id" and HAS_ARGON2:
        try:
            raw_hash = argon2.low_level.hash_secret_raw(
                secret=pw_bytes,
                salt=auth_salt,
                time_cost=ARGON2_TIME_COST,
                memory_cost=ARGON2_MEMORY_COST,
                parallelism=ARGON2_PARALLELISM,
                hash_len=32,
                type=argon2.low_level.Type.ID
            )
            return base64.b64encode(raw_hash).decode("utf-8")
        except Exception:
            pass
            
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=auth_salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.b64encode(kdf.derive(pw_bytes)).decode("utf-8")


def constant_time_compare(val1: str | bytes, val2: str | bytes) -> bool:
    """
    Constant-time comparison to prevent side-channel timing attacks.
    """
    if isinstance(val1, str):
        val1 = val1.encode("utf-8")
    if isinstance(val2, str):
        val2 = val2.encode("utf-8")
    return hmac.compare_digest(val1, val2)


# ============================================================================
# Authenticated Symmetric Encryption (AES-256-GCM)
# ============================================================================

def encrypt_aes_gcm(
    plaintext: str,
    key: bytes,
    associated_data: Optional[bytes] = None
) -> Tuple[str, str]:
    """
    Encrypt plaintext string using AES-256-GCM authenticated cipher.
    
    Returns:
        (ciphertext_b64, nonce_b64)
        Note: The 16-byte authentication tag is automatically appended 
        to the ciphertext by AESGCM and verified during decryption.
    """
    if not isinstance(key, bytes) or len(key) != AES_KEY_BYTES:
        raise ValueError(f"AES key must be exactly {AES_KEY_BYTES} bytes.")
        
    nonce = os.urandom(GCM_NONCE_BYTES)
    aesgcm = AESGCM(key)
    
    plaintext_bytes = plaintext.encode("utf-8")
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext_bytes, associated_data)
    
    ciphertext_b64 = base64.b64encode(ciphertext_with_tag).decode("utf-8")
    nonce_b64 = base64.b64encode(nonce).decode("utf-8")
    
    return ciphertext_b64, nonce_b64


def decrypt_aes_gcm(
    ciphertext_b64: str,
    nonce_b64: str,
    key: bytes,
    associated_data: Optional[bytes] = None
) -> str:
    """
    Decrypt base64-encoded ciphertext using AES-256-GCM authenticated cipher.
    
    Raises:
        ValueError: If key, nonce, or ciphertext is invalid or tampered.
    """
    if not isinstance(key, bytes) or len(key) != AES_KEY_BYTES:
        raise ValueError(f"AES key must be exactly {AES_KEY_BYTES} bytes.")
        
    try:
        ciphertext_with_tag = base64.b64decode(ciphertext_b64.encode("utf-8"))
        nonce = base64.b64decode(nonce_b64.encode("utf-8"))
    except Exception as e:
        raise ValueError(f"Base64 decoding failed: {e}")
        
    aesgcm = AESGCM(key)
    try:
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, associated_data)
        return decrypted_bytes.decode("utf-8")
    except InvalidTag:
        raise ValueError("Decryption failed: Authentication tag verification failed. Data has been tampered with or key is incorrect.")
    except Exception as e:
        raise ValueError(f"Decryption error: {e}")


# ============================================================================
# High-Entropy Password Generation & Strength Evaluation
# ============================================================================

def generate_secure_password(
    length: int = 18,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = True
) -> str:
    """
    Generate cryptographically strong random password using CSPRNG.
    Guarantees at least one character from each selected class.
    """
    length = max(8, length)
    
    lower_chars = string.ascii_lowercase
    upper_chars = string.ascii_uppercase
    digit_chars = string.digits
    symbol_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    if exclude_ambiguous:
        ambiguous = "il1Lo0O"
        lower_chars = "".join(c for c in lower_chars if c not in ambiguous)
        upper_chars = "".join(c for c in upper_chars if c not in ambiguous)
        digit_chars = "".join(c for c in digit_chars if c not in ambiguous)
        symbol_chars = symbol_chars.replace("|", "")
        
    categories = []
    guaranteed = []
    
    if use_lower and lower_chars:
        categories.append(lower_chars)
        guaranteed.append(secrets.choice(lower_chars))
    if use_upper and upper_chars:
        categories.append(upper_chars)
        guaranteed.append(secrets.choice(upper_chars))
    if use_digits and digit_chars:
        categories.append(digit_chars)
        guaranteed.append(secrets.choice(digit_chars))
    if use_symbols and symbol_chars:
        categories.append(symbol_chars)
        guaranteed.append(secrets.choice(symbol_chars))
        
    if not categories:
        # Fallback to standard alphanumeric
        categories.append(string.ascii_letters + string.digits)
        guaranteed.append(secrets.choice(string.ascii_letters))
        
    full_pool = "".join(categories)
    remaining_len = length - len(guaranteed)
    
    random_chars = [secrets.choice(full_pool) for _ in range(remaining_len)]
    combined = guaranteed + random_chars
    
    # Secure in-place shuffle using Fisher-Yates with CSPRNG
    for i in range(len(combined) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        combined[i], combined[j] = combined[j], combined[i]
        
    return "".join(combined)


def calculate_entropy(password: str) -> Dict[str, Any]:
    """
    Compute theoretical Shannon and character pool entropy in bits.
    Formula: Entropy = L * log2(R)
    """
    if not password:
        return {
            "entropy_bits": 0.0,
            "pool_size": 0,
            "length": 0,
            "strength": "None",
            "score": 0,
            "crack_time_estimate": "Instant"
        }
        
    length = len(password)
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    has_other = any(ord(c) > 127 for c in password)
    
    pool_size = 0
    if has_lower:
        pool_size += 26
    if has_upper:
        pool_size += 26
    if has_digit:
        pool_size += 10
    if has_symbol:
        pool_size += 32
    if has_other:
        pool_size += 64
        
    pool_size = max(pool_size, 1)
    entropy_bits = round(length * math.log2(pool_size), 1)
    
    # Assess strength category
    if entropy_bits < 40 or length < 8:
        strength = "Very Weak"
        score = 20
        crack_time = "Seconds"
    elif entropy_bits < 60 or length < 10:
        strength = "Weak"
        score = 45
        crack_time = "Hours / Days"
    elif entropy_bits < 80 or length < 14:
        strength = "Moderate"
        score = 70
        crack_time = "Years"
    elif entropy_bits < 100:
        strength = "Strong"
        score = 90
        crack_time = "Centuries"
    else:
        strength = "Very Strong"
        score = 100
        crack_time = "Billions of Years"
        
    return {
        "entropy_bits": entropy_bits,
        "pool_size": pool_size,
        "length": length,
        "strength": strength,
        "score": score,
        "crack_time_estimate": crack_time
    }
