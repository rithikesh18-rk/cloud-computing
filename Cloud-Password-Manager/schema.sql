-- ============================================================================
-- Zero-Knowledge Cloud Password Manager & Vault Database Schema
-- Architecture: Zero-Knowledge Client-Side AES-256-GCM & Argon2id / PBKDF2
-- ============================================================================

-- Table: users
-- Stores user identity, authentication verifier, and KDF configuration.
-- ZERO-KNOWLEDGE GUARANTEE:
-- The server stores auth_verifier (derived via independent salt) to authenticate,
-- but NEVER receives or stores the vault encryption key or plaintext master password.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    auth_verifier TEXT NOT NULL,         -- Argon2id/PBKDF2 hash of master password + auth_salt
    kdf_salt TEXT NOT NULL,              -- Base64 salt used client-side for Vault Key derivation
    auth_salt TEXT NOT NULL,             -- Base64 salt used for Master Password authentication
    kdf_algorithm TEXT DEFAULT 'argon2id', -- Key derivation algorithm ('argon2id' or 'pbkdf2_sha256')
    kdf_iterations INTEGER DEFAULT 600000, -- Iteration count / memory parameters
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: vault_items
-- Stores encrypted credentials.
-- ZERO-KNOWLEDGE GUARANTEE:
-- Passwords and sensitive notes are strictly stored as AES-256-GCM ciphertext
-- with dedicated 12-byte initialization vectors (nonce) and 16-byte authentication tags.
CREATE TABLE IF NOT EXISTS vault_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    username TEXT,
    ciphertext TEXT NOT NULL,            -- Base64 AES-256-GCM encrypted password + tag
    nonce_iv TEXT NOT NULL,              -- Base64 12-byte initialization vector (CSPRNG)
    notes_ciphertext TEXT,               -- Base64 AES-256-GCM encrypted notes
    notes_nonce TEXT,                    -- Base64 12-byte initialization vector for notes
    url TEXT,                            -- Associated service URL
    category TEXT DEFAULT 'Login',       -- Category: Login, Cloud API Key, Card, Secure Note
    is_favorite INTEGER DEFAULT 0,       -- 1 if pinned / favorite, 0 otherwise
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: audit_logs
-- Immutable tamper-evident audit trail of vault operations.
-- NEVER records plaintext credentials, keys, or sensitive payloads.
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,                -- E.g., 'VAULT_UNLOCKED', 'ITEM_ADDED', 'DECRYPT_ATTEMPT'
    status TEXT NOT NULL,                -- 'SUCCESS', 'FAILURE', 'WARNING'
    details TEXT,                        -- Sanitized non-sensitive metadata (e.g. record ID)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for performance & security filtering
CREATE INDEX IF NOT EXISTS idx_vault_items_user_id ON vault_items(user_id);
CREATE INDEX IF NOT EXISTS idx_vault_items_category ON vault_items(category);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
