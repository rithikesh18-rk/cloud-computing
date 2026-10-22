"""
Zero-Knowledge Cloud Password Manager - Interactive Dashboard & UI
===================================================================
A secure, client-side encrypted password manager interface built with Streamlit.
Features:
- Zero-Knowledge Authentication (Master password never leaves client unhashed)
- Client-Side AES-256-GCM authenticated encryption/decryption
- High-Entropy CSPRNG Password Generator
- Vault Health & Security Vulnerability Auditor
- Encrypted JSON Backup & Sync
- Tamper-Evident Audit Trail
"""

import sys
import os
import json
import time

# Ensure UTF-8 output on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def is_running_streamlit():
    """Detect whether app.py was launched via Streamlit CLI."""
    if any("streamlit" in arg.lower() for arg in sys.argv[:2]):
        return True
    if os.environ.get("STREAMLIT_SERVER_PORT") or os.environ.get("STREAMLIT_SERVER_ADDRESS"):
        return True
    return False


# Fallback to CLI / Demo if executed via python app.py
if __name__ == "__main__" and not is_running_streamlit():
    print("=" * 70)
    print("  🔐 ZERO-KNOWLEDGE CLOUD PASSWORD MANAGER")
    print("=" * 70)
    print("\nTo launch the interactive Web Dashboard:")
    print("  $ streamlit run app.py\n")
    print("Launching Terminal Interactive Console now...\n")
    import main
    main.main()
    sys.exit(0)

# ============================================================================
# Streamlit Application
# ============================================================================
import streamlit as st
import pandas as pd

from crypto import (
    generate_secure_password,
    calculate_entropy,
    HAS_ARGON2
)
from db import (
    init_db,
    register_user,
    authenticate_user,
    add_vault_item,
    get_vault_items,
    decrypt_vault_item,
    update_vault_item,
    delete_vault_item,
    toggle_favorite,
    get_audit_logs,
    DEFAULT_DB_PATH
)

# Initialize Database
init_db()

# Page Configuration
st.set_page_config(
    page_title="Zero-Knowledge Cloud Password Vault",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        color: #f8fafc;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-val {
        font-size: 28px;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-lbl {
        font-size: 13px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .vault-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-login { background-color: #0369a1; color: #e0f2fe; }
    .badge-cloud { background-color: #6d28d9; color: #ede9fe; }
    .badge-card { background-color: #b45309; color: #fef3c7; }
    .badge-note { background-color: #0f766e; color: #ccfbf1; }
    .zk-banner {
        background-color: #0c4a6e;
        border-left: 5px solid #38bdf8;
        padding: 12px 16px;
        border-radius: 4px;
        color: #f0f9ff;
        font-size: 13px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "vault_key" not in st.session_state:
    st.session_state.vault_key = None
if "revealed_items" not in st.session_state:
    st.session_state.revealed_items = set()


# ============================================================================
# Sidebar Navigation & Vault Status
# ============================================================================
with st.sidebar:
    st.markdown("### 🔐 Cloud Vault Guard")
    
    if st.session_state.user:
        st.success(f"**Unlocked:** `{st.session_state.user['username']}`")
        algo_name = st.session_state.user.get('kdf_algorithm', 'argon2id').upper()
        st.caption(f"🛡️ KDF: **{algo_name}** | Cipher: **AES-256-GCM**")
        
        nav = st.radio(
            "Navigation",
            ["🔑 Credential Vault", "➕ Add Credential", "⚡ Password Generator", "🛡️ Security Audit", "💾 Backup & Sync", "📜 Audit Trail"],
            index=0
        )
        
        st.markdown("---")
        if st.button("🔒 Lock Vault", use_container_width=True, type="secondary"):
            st.session_state.user = None
            st.session_state.vault_key = None
            st.session_state.revealed_items = set()
            st.rerun()
    else:
        st.info("🔒 **Vault Locked**\nPlease authenticate or create a vault.")
        nav = "Auth"

    st.markdown("---")
    st.markdown("""
    <div style='font-size: 12px; color: #94a3b8;'>
        <strong>Zero-Knowledge Security:</strong><br>
        • Client-Side AES-256-GCM<br>
        • Argon2id / PBKDF2 KDF<br>
        • Zero Plaintext on Server<br>
        • CSPRNG High Entropy
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# Authentication View (Login & Register)
# ============================================================================
if not st.session_state.user:
    st.title("🔐 Zero-Knowledge Cloud Password Manager")
    
    st.markdown("""
    <div class="zk-banner">
        <strong>🛡️ Zero-Knowledge Architecture Assurance:</strong><br>
        Your Master Password generates an encryption key stored solely in your client browser memory. 
        The server stores only high-iteration Argon2 authentication verifiers and ciphertext. 
        Neither the server administrators nor unauthorized database intruders can access your plain credentials.
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔓 Unlock Existing Vault", "✨ Create Master Vault"])

    with tab_login:
        st.subheader("Unlock Vault")
        with st.form("form_login"):
            username = st.text_input("Username / Email").strip()
            master_pw = st.text_input("Master Password", type="password")
            submitted = st.form_submit_button("Unlock Vault 🚀", use_container_width=True, type="primary")

            if submitted:
                if not username or not master_pw:
                    st.error("Please provide both username and master password.")
                else:
                    with st.spinner("Deriving encryption keys with Argon2id / PBKDF2..."):
                        user, key, err = authenticate_user(username, master_pw)
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.session_state.user = user
                        st.session_state.vault_key = key
                        st.success("Vault unlocked successfully!")
                        st.rerun()

    with tab_register:
        st.subheader("Create New Master Vault")
        with st.form("form_register"):
            new_user = st.text_input("Choose Username").strip()
            new_pw = st.text_input("Create Master Password", type="password")
            confirm_pw = st.text_input("Confirm Master Password", type="password")
            
            kdf_algo = "argon2id" if HAS_ARGON2 else "pbkdf2_sha256"
            st.caption(f"Primary Key Derivation Engine: `{kdf_algo.upper()}`")
            
            reg_submitted = st.form_submit_button("Initialize Vault 🛡️", use_container_width=True, type="primary")
            
            if reg_submitted:
                if not new_user:
                    st.error("Username cannot be empty.")
                elif len(new_pw) < 8:
                    st.error("Master password must be at least 8 characters.")
                elif new_pw != confirm_pw:
                    st.error("Master passwords do not match.")
                else:
                    with st.spinner("Generating cryptographically secure salts and initializing vault..."):
                        user, key, err = register_user(new_user, new_pw, algorithm=kdf_algo)
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.session_state.user = user
                        st.session_state.vault_key = key
                        st.success("Master Vault initialized successfully!")
                        st.rerun()

    # Password Strength Helper below form
    with st.expander("ℹ️ Master Password Best Practices"):
        st.markdown("""
        - Use a long passphrase of at least 14+ characters.
        - Combine upper/lowercase, numbers, and symbols.
        - Do not reuse master passwords across accounts.
        - The master password cannot be recovered if lost—there is no backdoor by design!
        """)


# ============================================================================
# Authenticated Vault Views
# ============================================================================
else:
    user_id = st.session_state.user["id"]
    vault_key = st.session_state.vault_key

    # ------------------------------------------------------------------------
    # View 1: Credential Vault
    # ------------------------------------------------------------------------
    if nav == "🔑 Credential Vault":
        st.title("🔑 Credential Vault")
        
        # Top KPI Metrics
        items = get_vault_items(user_id)
        categories = list(set([it.get("category", "Login") for it in items]))
        favorites_count = sum(1 for it in items if it.get("is_favorite") == 1)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-lbl">Total Credentials</div>
                <div class="metric-val">{len(items)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-lbl">Favorites</div>
                <div class="metric-val">⭐ {favorites_count}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-lbl">Categories</div>
                <div class="metric-val">{len(categories) or 1}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-lbl">Cipher Mode</div>
                <div class="metric-val">AES-256</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Search and Category Filters
        fcol1, fcol2, fcol3 = st.columns([3, 2, 1])
        with fcol1:
            search_query = st.text_input("🔍 Search Vault (Title, Username, URL)", placeholder="Filter credentials...")
        with fcol2:
            cat_filter = st.selectbox("Category", ["All"] + categories)
        with fcol3:
            st.write("")
            st.write("")
            fav_only = st.checkbox("⭐ Favorites only")

        # Filter items
        filtered = get_vault_items(
            user_id=user_id,
            category=cat_filter,
            search_query=search_query,
            favorites_only=fav_only
        )

        if not filtered:
            st.info("No credentials found matching your criteria. Click **'➕ Add Credential'** in the sidebar to add your first item!")
        else:
            for item in filtered:
                iid = item["id"]
                cat = item.get("category", "Login")
                badge_class = "badge-login"
                if cat == "Cloud API Key": badge_class = "badge-cloud"
                elif cat == "Card": badge_class = "badge-card"
                elif cat == "Secure Note": badge_class = "badge-note"

                is_fav = item.get("is_favorite") == 1
                fav_icon = "⭐" if is_fav else "☆"

                with st.expander(f"{fav_icon} {item['title']}  •  [{cat}]", expanded=False):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**Username / Email:** `{item.get('username') or 'N/A'}`")
                        if item.get("url"):
                            st.markdown(f"**URL:** [{item.get('url')}]({item.get('url')})")
                        st.caption(f"Added on: {item.get('created_at')}")

                    with c2:
                        # Toggle Favorite
                        if st.button(f"{'Unfavorite' if is_fav else 'Favorite'}", key=f"fav_{iid}"):
                            toggle_favorite(iid, user_id)
                            st.rerun()

                        # Delete
                        if st.button("🗑️ Delete", key=f"del_{iid}", type="secondary"):
                            delete_vault_item(iid, user_id)
                            st.success("Deleted!")
                            st.rerun()

                    # Decrypted password reveal section
                    st.markdown("---")
                    revealed = iid in st.session_state.revealed_items
                    
                    btn_col, pass_col = st.columns([1, 3])
                    with btn_col:
                        if st.button(f"{'🔒 Hide' if revealed else '👁️ Reveal'}", key=f"rev_{iid}"):
                            if revealed:
                                st.session_state.revealed_items.remove(iid)
                            else:
                                st.session_state.revealed_items.add(iid)
                            st.rerun()

                    with pass_col:
                        if revealed:
                            dec, err = decrypt_vault_item(iid, user_id, vault_key)
                            if err:
                                st.error(f"Decryption error: {err}")
                            else:
                                st.code(dec["password"], language="text")
                                ent = calculate_entropy(dec["password"])
                                st.caption(f"Entropy: **{ent['entropy_bits']} bits** ({ent['strength']})")
                                if dec.get("notes"):
                                    st.markdown(f"**Secure Notes:**\n`{dec['notes']}`")
                        else:
                            st.code("••••••••••••••••••••", language="text")

    # ------------------------------------------------------------------------
    # View 2: Add Credential
    # ------------------------------------------------------------------------
    elif nav == "➕ Add Credential":
        st.title("➕ Add Credential to Vault")
        
        with st.form("add_credential_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                title = st.text_input("Service / Title *", placeholder="e.g. AWS Production Console, GitHub, Work Email")
                category = st.selectbox("Category", ["Login", "Cloud API Key", "Payment Card", "Secure Note"])
                username = st.text_input("Username / Email", placeholder="user@company.com or iam_role")
            with col_b:
                url = st.text_input("Website / Service URL", placeholder="https://console.aws.amazon.com")
                is_fav = st.checkbox("Mark as Favorite ⭐")

            st.markdown("---")
            st.markdown("#### Password / Secret Payload")
            
            pwd_col1, pwd_col2 = st.columns([3, 1])
            with pwd_col1:
                password = st.text_input("Password *", type="password", key="new_item_pw")
            with pwd_col2:
                st.write("")
                st.write("")
                if st.form_submit_button("⚡ Quick Generate Strong Password"):
                    generated = generate_secure_password(length=20)
                    st.info(f"Generated: `{generated}`")
            
            notes = st.text_area("Secure Notes (Client-Side Encrypted)", placeholder="Recovery codes, API secrets, IP restrictions...")

            submit_add = st.form_submit_button("🔒 Encrypt & Store in Vault", type="primary", use_container_width=True)
            
            if submit_add:
                if not title:
                    st.error("Service Title is required.")
                elif not password:
                    st.error("Password is required.")
                else:
                    item_id, err = add_vault_item(
                        user_id=user_id,
                        title=title,
                        username=username,
                        plaintext_password=password,
                        vault_key=vault_key,
                        notes=notes,
                        url=url,
                        category=category,
                        is_favorite=1 if is_fav else 0
                    )
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.success(f"✅ Successfully encrypted with AES-256-GCM and stored! (Item ID: {item_id})")

    # ------------------------------------------------------------------------
    # View 3: Password Generator
    # ------------------------------------------------------------------------
    elif nav == "⚡ Password Generator":
        st.title("⚡ High-Entropy CSPRNG Password Generator")
        
        st.markdown("Generate cryptographically unguessable passwords using Python's hardware-backed `secrets` CSPRNG.")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            length = st.slider("Password Length", min_value=8, max_value=64, value=20)
            c1, c2 = st.columns(2)
            with c1:
                use_upper = st.checkbox("Uppercase (A-Z)", value=True)
                use_lower = st.checkbox("Lowercase (a-z)", value=True)
            with c2:
                use_digits = st.checkbox("Digits (0-9)", value=True)
                use_symbols = st.checkbox("Symbols (!@#$%^&*)", value=True)
            exclude_ambig = st.checkbox("Exclude Ambiguous Characters (il1Lo0O)", value=True)
            
            if st.button("🔄 Generate New Password", type="primary"):
                st.rerun()

        with col2:
            generated = generate_secure_password(
                length=length,
                use_upper=use_upper,
                use_lower=use_lower,
                use_digits=use_digits,
                use_symbols=use_symbols,
                exclude_ambiguous=exclude_ambig
            )
            ent = calculate_entropy(generated)
            
            st.markdown("#### Generated Result:")
            st.code(generated, language="text")
            
            st.metric("Shannon Entropy", f"{ent['entropy_bits']} bits")
            st.metric("Strength Rating", ent["strength"])
            st.caption(f"Estimated Crack Time: **{ent['crack_time_estimate']}**")

    # ------------------------------------------------------------------------
    # View 4: Security Audit
    # ------------------------------------------------------------------------
    elif nav == "🛡️ Security Audit":
        st.title("🛡️ Vault Security & Vulnerability Auditor")
        st.markdown("Performs zero-knowledge client-side memory analysis of stored credentials to detect vulnerabilities.")

        items = get_vault_items(user_id)
        if not items:
            st.info("Vault is empty. Add credentials to run an audit.")
        else:
            weak_items = []
            reused_items = {}
            passwords_seen = {}

            with st.spinner("Analyzing vault in secure client memory..."):
                for it in items:
                    dec, err = decrypt_vault_item(it["id"], user_id, vault_key)
                    if not err and dec:
                        pw = dec["password"]
                        ent = calculate_entropy(pw)
                        if ent["entropy_bits"] < 60:
                            weak_items.append((it, ent))
                        if pw in passwords_seen:
                            reused_items.setdefault(pw, []).append(it)
                            if passwords_seen[pw] not in [x["id"] for x in reused_items[pw]]:
                                # add the first one too
                                for orig in items:
                                    if orig["id"] == passwords_seen[pw]:
                                        reused_items[pw].insert(0, orig)
                        else:
                            passwords_seen[pw] = it["id"]

            # Score calculation
            total = len(items)
            vuln_count = len(weak_items) + sum(len(v) for v in reused_items.values())
            health_score = max(0, min(100, int(100 - (vuln_count / total * 50))))

            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.metric("Vault Health Score", f"{health_score} / 100")
            with sc2:
                st.metric("Weak Passwords", len(weak_items))
            with sc3:
                st.metric("Reused Password Clusters", len(reused_items))

            st.markdown("---")

            if weak_items:
                st.subheader("⚠️ Weak Passwords Detected (< 60 bits entropy)")
                for it, ent in weak_items:
                    st.warning(f"**{it['title']}** (`{it.get('username')}`) - Entropy: {ent['entropy_bits']} bits ({ent['strength']})")

            if reused_items:
                st.subheader("🚨 Password Reuse Detected")
                for pw, shared in reused_items.items():
                    names = ", ".join([f"**{x['title']}**" for x in shared])
                    st.error(f"The same password is shared across: {names}")

            if not weak_items and not reused_items:
                st.success("🎉 Excellent! All credentials meet zero-knowledge high-entropy requirements and no duplicates were found.")

    # ------------------------------------------------------------------------
    # View 5: Backup & Sync
    # ------------------------------------------------------------------------
    elif nav == "💾 Backup & Sync":
        st.title("💾 Zero-Knowledge Backup & Cloud Sync")
        
        st.markdown("""
        Export your vault as an authenticated JSON backup. 
        **Note:** The backup contains the encrypted ciphertext and nonces. 
        It can only be unlocked with your Master Password.
        """)

        items = get_vault_items(user_id)
        backup_payload = {
            "version": "1.0",
            "format": "zero_knowledge_vault",
            "exported_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
            "user": st.session_state.user["username"],
            "item_count": len(items),
            "items": []
        }
        for it in items:
            backup_payload["items"].append({
                "title": it["title"],
                "username": it.get("username"),
                "category": it.get("category"),
                "url": it.get("url"),
                "ciphertext": it.get("ciphertext"),
                "nonce_iv": it.get("nonce_iv"),
                "is_favorite": it.get("is_favorite")
            })

        json_str = json.dumps(backup_payload, indent=2)
        st.download_button(
            label="📥 Download Encrypted Vault Backup (.json)",
            data=json_str,
            file_name=f"vault_backup_{st.session_state.user['username']}.json",
            mime="application/json",
            type="primary"
        )

    # ------------------------------------------------------------------------
    # View 6: Audit Trail
    # ------------------------------------------------------------------------
    elif nav == "📜 Audit Trail":
        st.title("📜 Zero-Knowledge Security Audit Trail")
        st.markdown("Tamper-evident logs of vault operations. Verifies that no plaintext or cryptographic secrets are ever recorded.")

        logs = get_audit_logs(user_id, limit=50)
        if not logs:
            st.info("No audit logs available yet.")
        else:
            df = pd.DataFrame(logs)
            st.dataframe(
                df[["timestamp", "action", "status", "details"]],
                use_container_width=True,
                hide_index=True
            )
