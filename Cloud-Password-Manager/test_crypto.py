"""
Automated Test Suite for Zero-Knowledge Cryptographic Operations & Persistence
"""

import os
import pytest
from crypto import (
    generate_salt,
    derive_vault_key,
    hash_master_auth,
    encrypt_aes_gcm,
    decrypt_aes_gcm,
    generate_secure_password,
    calculate_entropy,
    constant_time_compare
)
from db import (
    init_db,
    register_user,
    authenticate_user,
    add_vault_item,
    get_vault_items,
    decrypt_vault_item,
    delete_vault_item,
    toggle_favorite,
    get_audit_logs
)

TEST_DB = "test_vault_pytest.db"


@pytest.fixture(autouse=True)
def cleanup():
    """Ensure clean database before and after each test."""
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass
    init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass


def test_key_derivation_deterministic():
    """Verify that identical password + salt yields identical key."""
    salt = generate_salt()
    key1 = derive_vault_key("MasterPass!2026", salt)
    key2 = derive_vault_key("MasterPass!2026", salt)
    assert key1 == key2
    assert len(key1) == 32


def test_zero_knowledge_salt_separation():
    """Ensure KDF salt and Auth salt produce mathematically independent outputs."""
    kdf_salt = generate_salt()
    auth_salt = generate_salt()
    
    vault_key = derive_vault_key("MasterSecret!456", kdf_salt)
    auth_verifier = hash_master_auth("MasterSecret!456", auth_salt)
    
    assert vault_key != auth_verifier.encode("utf-8")[:32]


def test_aes_gcm_roundtrip():
    """Verify encryption and decryption round-trip."""
    key = derive_vault_key("VaultKey", generate_salt())
    secret = "SuperSensitivePassword!99#"
    
    ciphertext, nonce = encrypt_aes_gcm(secret, key)
    decrypted = decrypt_aes_gcm(ciphertext, nonce, key)
    assert decrypted == secret


def test_aes_gcm_tamper_detection():
    """Verify that tampering with ciphertext triggers decryption failure (InvalidTag)."""
    key = derive_vault_key("VaultKey", generate_salt())
    secret = "ConfidentialData"
    ciphertext, nonce = encrypt_aes_gcm(secret, key)
    
    # Tamper with the ciphertext
    tampered_ciphertext = ("B" if ciphertext[0] == "A" else "A") + ciphertext[1:]
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_aes_gcm(tampered_ciphertext, nonce, key)


def test_aes_gcm_wrong_key():
    """Verify that attempting to decrypt with incorrect key fails."""
    key1 = derive_vault_key("KeyOne", generate_salt())
    key2 = derive_vault_key("KeyTwo", generate_salt())
    ciphertext, nonce = encrypt_aes_gcm("Payload", key1)
    
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_aes_gcm(ciphertext, nonce, key2)


def test_password_entropy_calculator():
    """Verify entropy calculations."""
    weak = calculate_entropy("123456")
    assert weak["strength"] == "Very Weak"
    assert weak["score"] <= 40
    
    strong = calculate_entropy("xK9#mQ2$vL8!pZ1@")
    assert strong["strength"] in ("Strong", "Very Strong")
    assert strong["entropy_bits"] >= 80


def test_password_generator():
    """Verify generated password meets length and diversity criteria."""
    pw = generate_secure_password(length=24, use_symbols=True)
    assert len(pw) == 24
    ent = calculate_entropy(pw)
    assert ent["entropy_bits"] > 100


def test_constant_time_comparison():
    """Verify hmac.compare_digest wrapper."""
    assert constant_time_compare("secret_hash_value", "secret_hash_value") is True
    assert constant_time_compare("secret_hash_value", "tampered_value") is False


def test_db_user_and_vault_lifecycle():
    """End-to-end test of user registration, authentication, vault item CRUD and audit."""
    user, key, err = register_user("charlie", "CharlieVaultMaster!2026", db_path=TEST_DB)
    assert err == ""
    assert user["username"] == "charlie"
    
    # Authenticate
    auth_user, auth_key, err = authenticate_user("charlie", "CharlieVaultMaster!2026", db_path=TEST_DB)
    assert err == ""
    assert auth_key == key
    
    # Add vault item
    item_id, err = add_vault_item(
        user_id=user["id"],
        title="Production DB",
        username="postgres_admin",
        plaintext_password="pg_super_secret_db_pass_2026!",
        vault_key=key,
        notes="High-priority AWS RDS cluster",
        url="https://aws.amazon.com/rds",
        category="Cloud API Key",
        is_favorite=1,
        db_path=TEST_DB
    )
    assert err == ""
    assert item_id is not None
    
    # Retrieve items
    items = get_vault_items(user["id"], db_path=TEST_DB)
    assert len(items) == 1
    assert items[0]["title"] == "Production DB"
    
    # Decrypt
    decrypted, err = decrypt_vault_item(item_id, user["id"], auth_key, db_path=TEST_DB)
    assert err == ""
    assert decrypted["password"] == "pg_super_secret_db_pass_2026!"
    assert decrypted["notes"] == "High-priority AWS RDS cluster"
    
    # Toggle favorite
    toggle_favorite(item_id, user["id"], db_path=TEST_DB)
    
    # Verify audit logs
    logs = get_audit_logs(user["id"], db_path=TEST_DB)
    actions = [l["action"] for l in logs]
    assert "USER_REGISTERED" in actions
    assert "VAULT_UNLOCKED" in actions
    assert "ITEM_CREATED" in actions
    assert "ITEM_DECRYPTED" in actions
