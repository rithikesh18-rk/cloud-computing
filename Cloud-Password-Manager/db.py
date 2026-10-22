"""
Zero-Knowledge Database & Vault Persistence Engine
===================================================
Manages SQLite storage for users, encrypted credential vaults, and immutable audit logs.
Strictly adheres to Zero-Knowledge principles:
- Plaintext passwords and notes are NEVER written to disk.
- Encryption keys are NEVER stored in the database.
- Master password verification is cryptographically separated from the vault encryption key.
"""

import os
import sqlite3
from typing import Dict, List, Optional, Tuple, Any

from crypto import (
    generate_salt,
    salt_to_b64,
    b64_to_salt,
    derive_vault_key,
    hash_master_auth,
    constant_time_compare,
    encrypt_aes_gcm,
    decrypt_aes_gcm
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "vault.db")


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Obtain a SQLite database connection with row factory configured."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize SQLite database tables and indexes."""
    schema_path = os.path.join(BASE_DIR, "schema.sql")
    conn = get_db_connection(db_path)
    try:
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        else:
            # Fallback schema execution
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    auth_verifier TEXT NOT NULL,
                    kdf_salt TEXT NOT NULL,
                    auth_salt TEXT NOT NULL,
                    kdf_algorithm TEXT DEFAULT 'argon2id',
                    kdf_iterations INTEGER DEFAULT 600000,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS vault_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    username TEXT,
                    ciphertext TEXT NOT NULL,
                    nonce_iv TEXT NOT NULL,
                    notes_ciphertext TEXT,
                    notes_nonce TEXT,
                    url TEXT,
                    category TEXT DEFAULT 'Login',
                    is_favorite INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                );
            """)
        conn.commit()
    finally:
        conn.close()


# ============================================================================
# Audit Logging (Zero-Knowledge: No sensitive plaintext ever recorded)
# ============================================================================

def log_audit(
    user_id: Optional[int],
    action: str,
    status: str,
    details: str = "",
    db_path: str = DEFAULT_DB_PATH
) -> None:
    """Record a security audit log event."""
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO audit_logs (user_id, action, status, details) VALUES (?, ?, ?, ?)",
            (user_id, action, status, details)
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def get_audit_logs(
    user_id: Optional[int] = None,
    limit: int = 50,
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """Retrieve historical security audit trail entries."""
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        if user_id is not None:
            cur.execute(
                "SELECT * FROM audit_logs WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            )
        else:
            cur.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


# ============================================================================
# User Authentication & Key Derivation
# ============================================================================

def register_user(
    username: str,
    master_password: str,
    algorithm: str = "argon2id",
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[Optional[Dict[str, Any]], Optional[bytes], str]:
    """
    Register a new vault user.
    Returns: (user_dict, vault_key, error_message)
    """
    username = username.strip()
    if not username:
        return None, None, "Username cannot be empty."
    if len(master_password) < 8:
        return None, None, "Master password must be at least 8 characters long."

    kdf_salt = generate_salt()
    auth_salt = generate_salt()
    
    auth_verifier = hash_master_auth(master_password, auth_salt, algorithm)
    vault_key = derive_vault_key(master_password, kdf_salt, algorithm)
    
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (username, auth_verifier, kdf_salt, auth_salt, kdf_algorithm)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, auth_verifier, salt_to_b64(kdf_salt), salt_to_b64(auth_salt), algorithm)
        )
        user_id = cur.lastrowid
        conn.commit()
        
        user_dict = {
            "id": user_id,
            "username": username,
            "kdf_algorithm": algorithm
        }
        log_audit(user_id, "USER_REGISTERED", "SUCCESS", f"User {username} registered", db_path)
        return user_dict, vault_key, ""
    except sqlite3.IntegrityError:
        return None, None, f"Username '{username}' already exists. Please sign in."
    except Exception as e:
        return None, None, f"Registration error: {e}"
    finally:
        conn.close()


def authenticate_user(
    username: str,
    master_password: str,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[Optional[Dict[str, Any]], Optional[bytes], str]:
    """
    Authenticate user against stored auth_verifier and derive local vault key.
    Returns: (user_dict, vault_key, error_message)
    """
    username = username.strip()
    if not username:
        return None, None, "Username required."
        
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        
        if not row:
            log_audit(None, "AUTH_FAILED", "FAILURE", f"Non-existent user '{username}'", db_path)
            return None, None, "Invalid username or master password."
            
        user = dict(row)
        auth_salt = b64_to_salt(user["auth_salt"])
        kdf_salt = b64_to_salt(user["kdf_salt"])
        algorithm = user.get("kdf_algorithm", "argon2id")
        
        computed_verifier = hash_master_auth(master_password, auth_salt, algorithm)
        if not constant_time_compare(computed_verifier, user["auth_verifier"]):
            log_audit(user["id"], "AUTH_FAILED", "FAILURE", "Incorrect master password", db_path)
            return None, None, "Invalid username or master password."
            
        # Derive vault key strictly client-side
        vault_key = derive_vault_key(master_password, kdf_salt, algorithm)
        user_dict = {
            "id": user["id"],
            "username": user["username"],
            "kdf_algorithm": algorithm,
            "created_at": user["created_at"]
        }
        log_audit(user["id"], "VAULT_UNLOCKED", "SUCCESS", "Client vault session initialized", db_path)
        return user_dict, vault_key, ""
    finally:
        conn.close()


# ============================================================================
# Credential Vault CRUD Operations
# ============================================================================

def add_vault_item(
    user_id: int,
    title: str,
    username: str,
    plaintext_password: str,
    vault_key: bytes,
    notes: Optional[str] = None,
    url: Optional[str] = None,
    category: str = "Login",
    is_favorite: int = 0,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[Optional[int], str]:
    """
    Encrypt and store a new credential item in the vault.
    Returns: (item_id, error_message)
    """
    if not title:
        return None, "Title is required."
    if not plaintext_password:
        return None, "Password is required."
        
    try:
        ciphertext, nonce_iv = encrypt_aes_gcm(plaintext_password, vault_key)
        
        notes_ciphertext = None
        notes_nonce = None
        if notes:
            notes_ciphertext, notes_nonce = encrypt_aes_gcm(notes, vault_key)
            
        conn = get_db_connection(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO vault_items (
                    user_id, title, username, ciphertext, nonce_iv,
                    notes_ciphertext, notes_nonce, url, category, is_favorite
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id, title, username, ciphertext, nonce_iv,
                    notes_ciphertext, notes_nonce, url, category, is_favorite
                )
            )
            item_id = cur.lastrowid
            conn.commit()
            
            log_audit(user_id, "ITEM_CREATED", "SUCCESS", f"Stored encrypted item id={item_id} category={category}", db_path)
            return item_id, ""
        finally:
            conn.close()
    except Exception as e:
        return None, f"Failed to add vault item: {e}"


def get_vault_items(
    user_id: int,
    category: Optional[str] = None,
    search_query: Optional[str] = None,
    favorites_only: bool = False,
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """Retrieve metadata and ciphertext of vault items (un-decrypted)."""
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        query = "SELECT id, user_id, title, username, url, category, is_favorite, created_at, updated_at FROM vault_items WHERE user_id = ?"
        params: List[Any] = [user_id]
        
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
            
        if favorites_only:
            query += " AND is_favorite = 1"
            
        if search_query:
            query += " AND (title LIKE ? OR username LIKE ? OR url LIKE ?)"
            wildcard = f"%{search_query}%"
            params.extend([wildcard, wildcard, wildcard])
            
        query += " ORDER BY is_favorite DESC, title ASC"
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def decrypt_vault_item(
    item_id: int,
    user_id: int,
    vault_key: bytes,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Fetch ciphertext and decrypt credentials using client's in-memory vault key.
    Returns: (decrypted_item_dict, error_message)
    """
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM vault_items WHERE id = ? AND user_id = ?", (item_id, user_id))
        row = cur.fetchone()
        if not row:
            return None, "Item not found or unauthorized access."
            
        item = dict(row)
        try:
            decrypted_password = decrypt_aes_gcm(item["ciphertext"], item["nonce_iv"], vault_key)
            decrypted_notes = ""
            if item.get("notes_ciphertext") and item.get("notes_nonce"):
                decrypted_notes = decrypt_aes_gcm(item["notes_ciphertext"], item["notes_nonce"], vault_key)
                
            item["password"] = decrypted_password
            item["notes"] = decrypted_notes
            
            log_audit(user_id, "ITEM_DECRYPTED", "SUCCESS", f"Decrypted item id={item_id}", db_path)
            return item, ""
        except Exception as e:
            log_audit(user_id, "ITEM_DECRYPT_FAILED", "FAILURE", f"Decryption failure on id={item_id}", db_path)
            return None, f"Decryption error: {e}"
    finally:
        conn.close()


def update_vault_item(
    item_id: int,
    user_id: int,
    title: str,
    username: str,
    plaintext_password: str,
    vault_key: bytes,
    notes: Optional[str] = None,
    url: Optional[str] = None,
    category: str = "Login",
    is_favorite: int = 0,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str]:
    """Update and re-encrypt an existing credential record."""
    try:
        ciphertext, nonce_iv = encrypt_aes_gcm(plaintext_password, vault_key)
        notes_ciphertext = None
        notes_nonce = None
        if notes:
            notes_ciphertext, notes_nonce = encrypt_aes_gcm(notes, vault_key)
            
        conn = get_db_connection(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE vault_items SET
                    title = ?, username = ?, ciphertext = ?, nonce_iv = ?,
                    notes_ciphertext = ?, notes_nonce = ?, url = ?,
                    category = ?, is_favorite = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (
                    title, username, ciphertext, nonce_iv,
                    notes_ciphertext, notes_nonce, url,
                    category, is_favorite, item_id, user_id
                )
            )
            conn.commit()
            log_audit(user_id, "ITEM_UPDATED", "SUCCESS", f"Updated encrypted item id={item_id}", db_path)
            return True, ""
        finally:
            conn.close()
    except Exception as e:
        return False, f"Failed to update item: {e}"


def delete_vault_item(
    item_id: int,
    user_id: int,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str]:
    """Permanently delete a vault credential item."""
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM vault_items WHERE id = ? AND user_id = ?", (item_id, user_id))
        conn.commit()
        log_audit(user_id, "ITEM_DELETED", "SUCCESS", f"Deleted item id={item_id}", db_path)
        return True, ""
    except Exception as e:
        return False, f"Failed to delete item: {e}"
    finally:
        conn.close()


def toggle_favorite(
    item_id: int,
    user_id: int,
    db_path: str = DEFAULT_DB_PATH
) -> bool:
    """Toggle the favorite flag of an item."""
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT is_favorite FROM vault_items WHERE id = ? AND user_id = ?", (item_id, user_id))
        row = cur.fetchone()
        if not row:
            return False
        new_val = 0 if row["is_favorite"] == 1 else 1
        cur.execute("UPDATE vault_items SET is_favorite = ? WHERE id = ? AND user_id = ?", (new_val, item_id, user_id))
        conn.commit()
        return True
    finally:
        conn.close()
