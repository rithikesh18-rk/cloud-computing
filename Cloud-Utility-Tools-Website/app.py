"""
Cloud Utility Tools - Visual Interactive Dashboard & Sysadmin Web Suite
========================================================================
Interactive multi-tool developer and sysadmin operations portal built with Streamlit.
Provides instant web UI for DNS, CIDR, JWT, Hashes, Format Converters, SSL, and Diagnostics.
"""

import sys
import os
import json
from datetime import datetime, timezone

# Ensure UTF-8 output on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to path
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


def is_running_streamlit():
    """Detect whether app.py was launched via Streamlit CLI."""
    if any("streamlit" in arg.lower() for arg in sys.argv[:2]):
        return True
    if os.environ.get("STREAMLIT_SERVER_PORT") or os.environ.get("STREAMLIT_SERVER_ADDRESS"):
        return True
    return False


# Fallback to CLI / Demo if executed via python app.py directly
if __name__ == "__main__" and not is_running_streamlit():
    print("=" * 75)
    print("  🛠️ CLOUD UTILITY TOOLS SUITE & WEB PLATFORM")
    print("=" * 75)
    print("\nTo launch the interactive Web Dashboard:")
    print("  $ streamlit run app.py\n")
    print("Or to launch the FastAPI REST service:")
    print("  $ uvicorn main:app --reload\n")
    print("Launching Terminal Diagnostic Suite now...\n")
    import main
    main.run_cli_audit()
    sys.exit(0)


# ============================================================================
# Streamlit Application
# ============================================================================
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Cloud Utility Tools Suite",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(120deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-success {
        background-color: #065f46;
        color: #34d399;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-warning {
        background-color: #78350f;
        color: #fbbf24;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-danger {
        background-color: #881337;
        color: #f43f5e;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar Navigation
st.sidebar.markdown("## 🛠️ Cloud Utility Tools")
st.sidebar.markdown("*Unified Cloud Sysadmin & Developer Suite*")
st.sidebar.markdown("---")

category = st.sidebar.radio(
    "Select Toolset:",
    [
        "🌐 Networking & DNS",
        "🔒 Security & Encoding",
        "🔄 Data & Format Converters",
        "🩺 System Diagnostics",
        "ℹ️ Platform & API Documentation",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("⚡ Cloud Computing Project 9 | Rithikesh S")
st.sidebar.caption("Dual Stack: Streamlit / FastAPI & Vue 3 / Vite")


# ============================================================================
# Category: 🌐 Networking & DNS
# ============================================================================
if category == "🌐 Networking & DNS":
    st.markdown('<div class="main-header">🌐 Networking & DNS Toolset</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">DNS lookup, CIDR subnetting, IP geolocation, and WHOIS domain registry queries.</div>', unsafe_allow_html=True)

    tab_dns, tab_cidr, tab_geo, tab_whois = st.tabs([
        "🔍 DNS Record Lookup",
        "📐 CIDR Subnet Calculator",
        "📍 IP Geolocation & ASN",
        "📋 WHOIS / RDAP Registry",
    ])

    with tab_dns:
        st.subheader("DNS Record Resolver")
        col1, col2 = st.columns([3, 1])
        with col1:
            domain_input = st.text_input("Target Domain or Hostname:", value="google.com", key="dns_domain")
        with col2:
            custom_ns = st.text_input("Custom Nameserver (Optional):", value="", placeholder="8.8.8.8", key="dns_ns")

        record_types = st.multiselect(
            "Resource Record Types:",
            ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SOA"],
            default=["A", "AAAA", "MX", "TXT"],
        )

        if st.button("Resolve DNS Records 🚀", type="primary", key="btn_dns"):
            with st.spinner("Resolving DNS records..."):
                res = dns_lookup(domain_input, record_types, nameserver=custom_ns if custom_ns else None)
                st.success(f"DNS Resolution Completed for **{res['domain']}** (Resolver: {res['resolver']})")

                for rtype, rinfo in res["records"].items():
                    with st.expander(f"**{rtype} Records** ({rinfo['count']} found, TTL: {rinfo['ttl']}s)", expanded=(rinfo['count'] > 0)):
                        if rinfo["count"] > 0:
                            if rtype == "MX":
                                st.dataframe(pd.DataFrame(rinfo["data"]))
                            else:
                                for item in rinfo["data"]:
                                    st.code(str(item), language="text")
                        else:
                            st.info(f"No {rtype} records found.")

                if res.get("errors"):
                    for k, err in res["errors"].items():
                        st.warning(f"Note ({k}): {err}")

    with tab_cidr:
        st.subheader("CIDR & Subnet Capacity Calculator")
        cidr_input = st.text_input("CIDR Block (IPv4 or IPv6):", value="10.240.0.0/22", key="cidr_in")

        if st.button("Calculate Subnet Boundaries 📐", type="primary", key="btn_cidr") or cidr_input:
            res = cidr_calculator(cidr_input)
            if res.get("valid"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Usable Host Capacity", f"{res['usable_hosts']:,}")
                c2.metric("Total Addresses", f"{res['total_addresses']:,}")
                c3.metric("Prefix Length", f"/{res['prefix_length']}")
                c4.metric("Network Type", "Private (RFC1918)" if res["is_private"] else "Public Internet")

                st.markdown("#### Subnet Boundary Table")
                df_cidr = pd.DataFrame([
                    {"Parameter": "Network Address", "Value": res["network_address"]},
                    {"Parameter": "Broadcast Address", "Value": res["broadcast_address"]},
                    {"Parameter": "Subnet Netmask", "Value": res["netmask"]},
                    {"Parameter": "Wildcard Mask", "Value": res["wildcard_mask"]},
                    {"Parameter": "First Usable Host", "Value": res["first_usable_ip"]},
                    {"Parameter": "Last Usable Host", "Value": res["last_usable_ip"]},
                    {"Parameter": "Binary Netmask", "Value": res["binary_netmask"]},
                ])
                st.table(df_cidr)
            else:
                st.error(res.get("error"))

    with tab_geo:
        st.subheader("IP Geolocation & Carrier Inspector")
        ip_in = st.text_input("IP Address or Domain:", value="1.1.1.1", key="geo_in")

        if st.button("Lookup Geolocation 📍", type="primary", key="btn_geo"):
            with st.spinner("Querying BGP & IP Geolocation registries..."):
                geo = ip_geolocation(ip_in)
                if geo.get("valid"):
                    g1, g2, g3 = st.columns(3)
                    g1.metric("Country", f"{geo.get('country')} ({geo.get('country_code', 'XX')})")
                    g2.metric("City / Region", f"{geo.get('city')}, {geo.get('region')}")
                    g3.metric("Autonomous System (ASN)", geo.get("asn", "N/A"))

                    st.json(geo)
                else:
                    st.error(geo.get("error"))

    with tab_whois:
        st.subheader("WHOIS & RDAP Domain Registration Inspector")
        whois_in = st.text_input("Domain or IP for RDAP Query:", value="github.com", key="whois_in")

        if st.button("Query RDAP Registry 📋", type="primary", key="btn_whois"):
            with st.spinner("Querying ICANN RDAP bootstrap servers..."):
                rd = whois_lookup(whois_in)
                st.json(rd)


# ============================================================================
# Category: 🔒 Security & Encoding
# ============================================================================
elif category == "🔒 Security & Encoding":
    st.markdown('<div class="main-header">🔒 Security & Encoding Toolset</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">JWT token inspection, Base64/URL encoding, cryptographic hashing, and high-entropy password generation.</div>', unsafe_allow_html=True)

    tab_jwt, tab_b64, tab_hash, tab_pwd = st.tabs([
        "🎫 JWT Token Inspector",
        "🔤 Base64 & URL Encoding",
        "#️⃣ Cryptographic Hashes",
        "🔑 Password Generator",
    ])

    with tab_jwt:
        st.subheader("JSON Web Token (JWT) Inspector")
        sample_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIENsb3VkIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxODkzNDU2MDAwfQ.P-aPzY4b7Q_oF5Y18b8iB3iNn-k3m_EXAMPLE_SIGNATURE"
        jwt_in = st.text_area("JWT Token String:", value=sample_jwt, height=100, key="jwt_input")
        jwt_secret = st.text_input("Verification Secret (Optional):", type="password", key="jwt_sec")

        if st.button("Decode & Validate Token 🎫", type="primary", key="btn_jwt") or jwt_in:
            j_res = decode_jwt(jwt_in, secret=jwt_secret if jwt_secret else None)
            if j_res.get("valid"):
                m1, m2, m3 = st.columns(3)
                m1.metric("Algorithm", j_res["algorithm"])
                m2.metric("Expiration Status", "Expired" if j_res["is_expired"] else "Valid / Active")
                m3.metric("Signature Check", "Passed" if "Verified" in j_res["signature_verification"] else "Unverified")

                st.markdown("#### Header")
                st.json(j_res["header"])
                st.markdown("#### Payload Claims")
                st.json(j_res["payload"])
                st.info(f"Status: {j_res['expiration_status']}")
            else:
                st.error(j_res.get("error"))

    with tab_b64:
        st.subheader("Base64 & URL Component Encoding / Decoding")
        b64_mode = st.radio("Operation Mode:", ["Base64 Encode", "Base64 Decode", "URL Encode", "URL Decode"], horizontal=True)
        url_safe = st.checkbox("URL-Safe Base64 (- and _ instead of + and /)", value=False)
        input_text = st.text_area("Input Text / Payload:", value="Cloud Computing Suite 2026", height=120)

        if st.button("Process Encoding / Decoding 🔤", type="primary", key="btn_b64"):
            if b64_mode == "Base64 Encode":
                out = encode_base64(input_text, url_safe=url_safe)
                st.text_area("Base64 Encoded Result:", value=out, height=100)
            elif b64_mode == "Base64 Decode":
                res = decode_base64(input_text, url_safe=url_safe)
                if res.get("success"):
                    st.text_area("Decoded Plaintext:", value=res.get("text") or res.get("hex"), height=100)
                    st.caption(f"Byte Length: {res['byte_length']} bytes | UTF-8: {res['is_utf8']}")
                else:
                    st.error(res.get("error"))
            elif b64_mode == "URL Encode":
                out = encode_url(input_text)
                st.text_area("URL Encoded Result:", value=out, height=100)
            elif b64_mode == "URL Decode":
                out = decode_url(input_text)
                st.text_area("URL Decoded Result:", value=out, height=100)

    with tab_hash:
        st.subheader("Cryptographic Hash Generator")
        hash_input = st.text_area("Input Payload / Text:", value="The quick brown fox jumps over the lazy dog", height=100)
        hmac_key = st.text_input("Optional HMAC Secret Key:", value="", type="password")

        if st.button("Compute Hashes #️⃣", type="primary", key="btn_hash") or hash_input:
            hashes = generate_hashes(hash_input, hmac_key=hmac_key if hmac_key else None)
            st.markdown(f"**SHA-256:** `{hashes['sha256']}`")
            st.markdown(f"**SHA-512:** `{hashes['sha512']}`")
            st.markdown(f"**MD5:** `{hashes['md5']}`")
            st.markdown(f"**SHA-1:** `{hashes['sha1']}`")
            if "hmac_sha256" in hashes:
                st.markdown(f"**HMAC-SHA256:** `{hashes['hmac_sha256']}`")

    with tab_pwd:
        st.subheader("CSPRNG High-Entropy Password & Secret Generator")
        col_len, col_opt = st.columns([1, 2])
        with col_len:
            pwd_len = st.slider("Password Length:", min_value=8, max_value=64, value=24)
        with col_opt:
            c1, c2, c3, c4 = st.columns(4)
            u_upper = c1.checkbox("A-Z", value=True)
            u_lower = c2.checkbox("a-z", value=True)
            u_digits = c3.checkbox("0-9", value=True)
            u_sym = c4.checkbox("!@#$", value=True)

        if st.button("Generate Secure Password 🔑", type="primary", key="btn_pwd"):
            p_res = generate_secure_password(length=pwd_len, use_upper=u_upper, use_lower=u_lower, use_digits=u_digits, use_symbols=u_sym)
            st.code(p_res["password"], language="text")
            ent = p_res["entropy"]
            st.success(f"Entropy: **{ent['bits']} bits** | Rating: **{ent['strength']}** | Brute-force estimate: **{ent['crack_time']}**")


# ============================================================================
# Category: 🔄 Data & Format Converters
# ============================================================================
elif category == "🔄 Data & Format Converters":
    st.markdown('<div class="main-header">🔄 Data & Format Converters</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">JSON, YAML, CSV conversions, validation, beautification, and cron expression parsing.</div>', unsafe_allow_html=True)

    tab_conv, tab_json, tab_cron = st.tabs([
        "🔀 JSON ↔ YAML ↔ CSV",
        "✨ JSON Beautifier & Minifier",
        "⏰ Cron Syntax Parser",
    ])

    with tab_conv:
        st.subheader("Format Transformation Engine")
        mode = st.selectbox("Select Conversion:", ["JSON to YAML", "YAML to JSON", "JSON to CSV", "CSV to JSON"])
        default_json = '{\n  "service": "CloudUtility",\n  "version": "1.0.0",\n  "tools": ["DNS", "CIDR", "JWT", "SSL"]\n}'
        conv_in = st.text_area("Input Content:", value=default_json, height=180)

        if st.button("Convert Format 🔀", type="primary", key="btn_conv"):
            if mode == "JSON to YAML":
                res = json_to_yaml(conv_in)
            elif mode == "YAML to JSON":
                res = yaml_to_json(conv_in)
            elif mode == "JSON to CSV":
                res = json_to_csv(conv_in)
            elif mode == "CSV to JSON":
                res = csv_to_json(conv_in)

            if res.get("success"):
                st.text_area("Converted Output:", value=res.get("output"), height=200)
            else:
                st.error(res.get("error"))

    with tab_json:
        st.subheader("JSON Validator, Beautifier & Minifier")
        j_text = st.text_area("JSON Payload:", value='{"name":"cloud-tools","active":true,"port":8000,"endpoints":["/api/dns","/api/cidr"]}', height=120)
        c1, c2 = st.columns(2)
        if c1.button("Format & Beautify ✨", type="primary"):
            f_res = format_json(j_text, indent=2, minify=False)
            if f_res.get("valid"):
                st.code(f_res["output"], language="json")
                st.caption(f"Elements: {f_res['element_count']} | Size: {f_res['formatted_size_bytes']} bytes")
            else:
                st.error(f_res.get("error"))

        if c2.button("Minify (Compress) 📦"):
            f_res = format_json(j_text, minify=True)
            if f_res.get("valid"):
                st.code(f_res["output"], language="json")
                st.caption(f"Minified Size: {f_res['formatted_size_bytes']} bytes")
            else:
                st.error(f_res.get("error"))

    with tab_cron:
        st.subheader("Cron Schedule Syntax Parser")
        cron_input = st.text_input("Cron Expression (5-field standard):", value="0 */3 * * 1-5", key="cron_in")

        if st.button("Parse Cron Schedule ⏰", type="primary", key="btn_cron") or cron_input:
            c_res = parse_cron(cron_input, num_runs=5)
            if c_res.get("valid"):
                st.info(f"**Plain-English Schedule:** {c_res['human_description']}")
                st.markdown("#### Next 5 Execution Timestamps (UTC)")
                for dt in c_res["next_executions"]:
                    st.markdown(f"- 🕒 `{dt}`")
            else:
                st.error(c_res.get("error"))


# ============================================================================
# Category: 🩺 System Diagnostics
# ============================================================================
elif category == "🩺 System Diagnostics":
    st.markdown('<div class="main-header">🩺 System & Cloud Diagnostics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">HTTP header posture inspection, SSL/TLS certificate auditing, and batch UUID generation.</div>', unsafe_allow_html=True)

    tab_http, tab_ssl, tab_uuid = st.tabs([
        "🛡️ HTTP Header Inspector",
        "🔐 SSL Certificate Checker",
        "🆔 UUID Generator",
    ])

    with tab_http:
        st.subheader("HTTP Response Header & Security Grader")
        target_url = st.text_input("Target URL:", value="https://github.com", key="http_url")

        if st.button("Probe Headers & Grade Security 🛡️", type="primary", key="btn_http"):
            with st.spinner("Probing HTTP headers and evaluating security posture..."):
                h_res = inspect_http_headers(target_url)
                if h_res.get("success"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("HTTP Status", f"{h_res['status_code']} {h_res['reason']}")
                    c2.metric("Latency", f"{h_res['latency_ms']} ms")
                    c3.metric("Security Header Grade", h_res["security_audit"]["grade"])

                    st.markdown("#### Security Header Compliance")
                    for header_name, check in h_res["security_audit"]["checks"].items():
                        st.markdown(f"- **{header_name}**: {'✅ Present' if check['present'] else '❌ Missing'} (`{check['value']}`)")

                    st.markdown("#### All Raw Response Headers")
                    st.json(h_res["headers"])
                else:
                    st.error(h_res.get("error"))

    with tab_ssl:
        st.subheader("SSL / TLS Certificate Health Checker")
        col_host, col_port = st.columns([3, 1])
        with col_host:
            ssl_host = st.text_input("Hostname or URL:", value="cloudflare.com", key="ssl_h")
        with col_port:
            ssl_port = st.number_input("TLS Port:", min_value=1, max_value=65535, value=443)

        if st.button("Inspect SSL/TLS Certificate 🔐", type="primary", key="btn_ssl"):
            with st.spinner("Establishing TLS handshake and parsing certificate..."):
                s_res = check_ssl_certificate(ssl_host, ssl_port)
                if s_res.get("valid"):
                    s1, s2, s3 = st.columns(3)
                    s1.metric("Issuer", s_res["issuer"])
                    s2.metric("Days Remaining", f"{s_res['days_remaining']} days")
                    s3.metric("Health", s_res["health_status"])

                    st.markdown(f"**Valid From:** {s_res['valid_from']}")
                    st.markdown(f"**Valid Until:** {s_res['valid_until']}")
                    st.markdown(f"**TLS Protocol:** {s_res['tls_version']} | **Cipher:** `{s_res['cipher_suite']}` ({s_res['cipher_bits']} bits)")
                    with st.expander(f"Subject Alternative Names ({s_res['total_sans']} SANs)"):
                        st.write(", ".join(s_res["subject_alt_names"]))
                else:
                    st.error(f"{s_res.get('health_status')}: {s_res.get('error')}")

    with tab_uuid:
        st.subheader("Batch UUID & Identifier Generator")
        u_ver = st.selectbox("UUID Version:", ["v4 (CSPRNG Random)", "v1 (Time & MAC Based)", "v5 (SHA-1 Name Based)"])
        u_count = st.slider("Number of UUIDs:", min_value=1, max_value=50, value=5)
        c_upper = st.checkbox("Uppercase (e.g. 550E8400...)", value=False)
        c_nohyphen = st.checkbox("Strip Hyphens (32-character hex)", value=False)

        ver_code = "v4" if "v4" in u_ver else ("v1" if "v1" in u_ver else "v5")
        if st.button("Generate UUIDs 🆔", type="primary", key="btn_uuid"):
            uuids = generate_uuids(count=u_count, version=ver_code, uppercase=c_upper, no_hyphens=c_nohyphen, namespace_dns="cloud.local")
            for u in uuids:
                st.code(u, language="text")


# ============================================================================
# Category: ℹ️ Platform & API Documentation
# ============================================================================
else:
    st.markdown('<div class="main-header">ℹ️ Cloud Utility Tools Documentation</div>', unsafe_allow_html=True)
    st.markdown("""
    ### Architecture Overview
    Cloud Utility Tools is a dual-stack developer and sysadmin web platform designed to eliminate reliance on ad-heavy, third-party formatting and diagnostic utilities.
    
    #### Core Architectural Guarantees:
    - **100% Client & Intranet Confidentiality:** No user payloads, JWT secrets, passwords, or network topologies are transmitted to external untrusted trackers.
    - **Dual-Stack Runtime:**
      1. **Python / Streamlit & FastAPI:** Interactive diagnostic UI + OpenAPI REST microservice.
      2. **Vue 3 / TypeScript / Vite:** Static single-page application with UnoCSS and client-side web workers.
    - **Container-Ready:** Production-grade `Dockerfile` and automated CI/CD compatibility.
    """)
    st.markdown("#### REST API Quickstart")
    st.code("""
# Launch FastAPI backend:
$ uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# OpenAPI Documentation:
http://127.0.0.1:8000/docs
    """, language="bash")
