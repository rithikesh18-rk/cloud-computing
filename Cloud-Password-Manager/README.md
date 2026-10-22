# Zero-Knowledge Cloud Password Manager & Vault

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![AES-256-GCM](https://img.shields.io/badge/Cipher-AES--256--GCM-00C853.svg?style=flat&logo=lock&logoColor=white)](https://csrc.nist.gov/publications/detail/sp/800-38d/final)
[![Argon2id](https://img.shields.io/badge/KDF-Argon2id%20%2F%20PBKDF2-blueviolet.svg?style=flat&logo=gnu-privacy-guard&logoColor=white)](https://www.rfc-editor.org/rfc/rfc9106)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-ACID_Vault-003B57.svg?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, zero-knowledge encrypted credential vault and cloud password manager. Built to eliminate the threat of centralized database breaches, unauthorized cloud provider access, and plaintext memory leaks through client-side authenticated cryptographic key derivation and hardware-backed authenticated symmetric encryption.

---

## 📌 Problem Statement

In distributed cloud environments, traditional credential vaults and third-party credential hosts pose catastrophic single points of failure:
- **Cloud Credential Leaks:** Unauthorized database dumps, stolen SQL backups, or misconfigured S3 buckets expose user credentials in cleartext if encryption keys are stored on the server side.
- **Insider & Third-Party Host Risks:** Untrusted cloud infrastructure providers, compromised hypervisors, and rogue administrators can intercept cleartext secrets traversing application memory.
- **Weak Key Derivation:** Legacy systems relying on weak hashes (MD5, SHA-1, un-salted SHA-256) succumb to GPU-accelerated dictionary and rainbow table attacks.

The **Zero-Knowledge Cloud Password Manager & Vault** solves these vulnerabilities by strictly decoupling identity authentication from credential decryption. The cloud server and database store **only ciphertext, random nonces, and independent salts**—the master password and derived encryption keys never leave local client memory unhashed.

---

## 🛡️ Security & Architecture Model

```
                    ZERO-KNOWLEDGE CRYPTOGRAPHIC WORKFLOW

 [ User Enters Master Password ]
               │
               ├─────────────────────────────────────────┐
               ▼ (Client-Side Only)                      ▼ (Independent Auth Path)
   [ Argon2id / PBKDF2 KDF ]                 [ Argon2id Auth Hasher ]
         + kdf_salt (16B)                          + auth_salt (16B)
               │                                         │
               ▼                                         ▼
   [ 256-bit AES Vault Key ]                     [ Auth Verifier Hash ]
   (Kept in Memory ONLY;                                 │
    NEVER sent to Server)                                ▼
               │                              [ Cloud SQLite / DB Server ]
               ▼                             (Validates login without key)
  [ AES-256-GCM Encrypt / Decrypt ]                      │
         + 12B Nonce/IV                                  │
         + 16B Auth Tag                                  ▼
               │                            [ Encrypted Vault Records ]
               └──────────────────────────► (Ciphertext + Nonce + Salts)
                                            * Server cannot decrypt *
```

### 1. Zero-Knowledge Architecture
- **Client-Side Key Derivation:** The master password is fed into memory-hard key derivation functions strictly in client memory. The derived 256-bit symmetric key is never transmitted across the network nor written to persistent storage.
- **Cryptographic Separation of Concerns:** Two mathematically independent salts (`kdf_salt` and `auth_salt`) generate two entirely separate cryptographic objects:
  1. **Vault Encryption Key:** Used locally for AES-256-GCM encryption/decryption.
  2. **Auth Verifier:** Sent to the database for identity verification. A compromised server database provides an attacker zero capability to reconstruct the vault key.

### 2. Cryptographic Primitives
- **Authenticated Symmetric Cipher:** **AES-256-GCM** (NIST SP 800-38D) provides both confidential encryption and Poly1305 authentication tags. Any unauthorized bit modification in storage triggers immediate cryptographic rejection (`InvalidTag`).
- **Memory-Hard Key Derivation:** **Argon2id** (RFC 9106) with 64 MB memory cost, 3 iterations, and 4 parallel lanes defends against ASIC and GPU rainbow cracking, with seamless fallback to **PBKDF2-HMAC-SHA256** (600,000 iterations, OWASP 2024 compliance).
- **CSPRNG Initialization Vectors:** Unique 96-bit (12-byte) initialization vectors are generated per-credential using hardware entropy (`os.urandom`), ensuring identical plaintext passwords yield completely distinct ciphertexts.

### 3. Credential Management & UX
- **Vault Operations:** Add, update, search, filter, and permanently delete credentials across categories (Logins, Cloud API Keys, Payment Cards, Secure Notes).
- **Client-Side Decryption on Demand:** Password fields are masked by default (`••••••••••••`). Clicking "Reveal" decrypts the payload in-memory with safety toggle timeouts.
- **High-Entropy Password Generator:** Hardware-backed CSPRNG (`secrets`) generates passwords up to 64 characters with configurable character classes (uppercase, lowercase, digits, symbols) and ambiguous character exclusions.
- **Shannon & Pool Entropy Calculator:** Computes real-time theoretical entropy ($E = L \times \log_2(R)$) and estimated brute-force crack time.

### 4. Cloud Vault Synchronization & Tamper-Evident Audit
- **Zero-Knowledge Backup:** Exports vault records into authenticated JSON snapshots containing only ciphertexts and nonces, safely portable across multi-device endpoints.
- **Immutable Security Audit Trail:** System events (`VAULT_UNLOCKED`, `ITEM_CREATED`, `ITEM_DECRYPTED`, `AUTH_FAILED`) are logged with timestamps and status, strictly excluding sensitive payloads or plaintext.

---

## 💻 Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Cryptography Core** | `cryptography` (pyca), `argon2-cffi` | AES-256-GCM AEAD, Argon2id, PBKDF2-SHA256, CSPRNG |
| **Frontend UI** | Streamlit 1.38+, Custom CSS | Interactive, responsive dark-mode security dashboard |
| **CLI & Engine** | Python 3.11+ | Dual-stack interactive console, benchmark suite, automation |
| **Database** | SQLite 3, Foreign Keys, ACID | Zero-knowledge relational vault storage and audit logs |
| **Upstream Compatibility** | Rust / Bitwarden / Vaultwarden | Enterprise self-hosted cloud backend compatibility |

---

## 📂 Project Directory Tree

```text
Cloud-Password-Manager/
│
├── app.py                      # Interactive Streamlit vault dashboard & web application
├── main.py                     # Dual-mode interactive CLI console & crypto benchmark auditor
├── crypto.py                   # Cryptographic engine (AES-256-GCM, Argon2id, PBKDF2, Entropy)
├── db.py                       # SQLite persistence layer, authentication verifier & audit logger
├── schema.sql                  # Database schema definitions with zero-knowledge constraints
├── test_crypto.py              # Automated pytest suite (key derivation, AES-GCM, tamper checks)
├── requirements.txt            # Pinned Python package dependencies
├── VAULTWARDEN_GUIDE.md        # Preserved upstream enterprise Rust vault documentation
│
├── docker/                     # Upstream multi-stage container deployment definitions
├── migrations/                 # Upstream relational schema migration scripts (PostgreSQL, SQLite, MySQL)
├── src/                        # Upstream Rust core Bitwarden API & WebSocket services
├── Cargo.toml                  # Upstream Rust package manifest
├── Dockerfile                  # Upstream container build specification
└── README.md                   # Dedicated zero-knowledge project overview & documentation
```

---

## ⚡ Quickstart Guide

### 1. Virtual Environment Setup

```bash
# Clone repository if not already local
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/Cloud-Password-Manager

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux / macOS:
# source venv/bin/activate
```

### 2. Dependency Installation

```bash
pip install -r requirements.txt
```

### 3. Run Application

#### Option A: Interactive Streamlit Web Dashboard
```bash
streamlit run app.py
```
*Access the local web vault at `http://localhost:8501`.*

#### Option B: Terminal Interactive Console & Crypto Benchmark
```bash
# Run interactive CLI console:
python main.py

# Run automated zero-knowledge cryptographic benchmark & audit:
python main.py --demo
```

#### Option C: Execute Automated Test Suite
```bash
pytest test_crypto.py -v
```

---

## 🔒 Security Audit & Best Practices Checklist

- [x] **Zero Plaintext Persistence:** No plaintext password, API secret, or notes payload is ever written to disk or recorded in log files.
- [x] **Constant-Time Verifications:** Master password authentication verifier comparisons utilize `hmac.compare_digest` to prevent side-channel timing attacks.
- [x] **Unique Nonce Guarantee:** AES-256-GCM nonces are 96-bit cryptographically secure pseudorandom numbers generated afresh per encryption operation, strictly preventing nonce reuse.
- [x] **Authenticity & Tamper Proofing:** 128-bit Poly1305 authentication tags ensure modified or corrupted database records are rejected automatically before decryption.
- [x] **Memory Scrubbing Hygiene:** Client memory references to derived symmetric keys are isolated in session scope and cleared immediately upon user vault lock or session termination.
- [x] **Independent Salt Derivations:** Separate CSPRNG salts prevent cross-domain key derivation or hash-table correlation between authentication credentials and encryption keys.
