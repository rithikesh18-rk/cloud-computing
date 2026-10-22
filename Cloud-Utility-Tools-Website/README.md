# 🛠️ Cloud Utility Tools Suite & Web Platform

A unified, production-ready developer and sysadmin web platform providing critical networking, security, data conversion, and system diagnostic utilities. Designed for cloud engineers, DevOps practitioners, and software architects who demand privacy, speed, and zero reliance on ad-heavy third-party websites.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Vue 3](https://img.shields.io/badge/Vue-3.0-4FC08D.svg?style=flat&logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF.svg?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)

---

## 📌 Problem Statement

Cloud engineers, developers, and DevOps practitioners frequently switch between disjointed, ad-heavy third-party sites for routine diagnostic and formatting tasks (e.g., pasting production JWT tokens into public decoders, formatting sensitive database JSON dumps, inspecting SSL certificates, or calculating VPC subnets). 

This workflow presents severe operational and security risks:
1. **Data Exfiltration & Privacy Exposure:** Pasting production authorization tokens, database configurations, and network architectures into untrusted web endpoints leaks proprietary data to third-party ad networks and aggregators.
2. **Context Switching & Friction:** Relying on separate sites for DNS, CIDR, hash calculation, and cron scheduling slows operational troubleshooting during live production incidents.
3. **Availability & Ad-Blocker Failure:** Third-party utility sites frequently degrade under corporate VPN firewalls, rate limits, and intrusive advertising trackers.

**The Solution:** A self-hosted, cloud-native utility platform providing instant client-side and backend processing with **100% data confidentiality**, unified navigation, an OpenAPI REST service, and a responsive web dashboard.

---

## 🚀 Integrated Toolsets

The suite is organized into four core functional domains:

### 1. 🌐 Networking & DNS
- **DNS Record Lookup:** Resolves standard DNS resource records (`A`, `AAAA`, `CNAME`, `MX`, `TXT`, `NS`, `SOA`) with TTL auditing, mail exchange preferences, and custom nameserver selection (e.g., Cloudflare `1.1.1.1`, Google `8.8.8.8`).
- **CIDR & Subnet Calculator:** Computes network boundaries, broadcast addresses, subnet masks, wildcard masks, and usable IP host capacities for IPv4 and IPv6 VPC allocations.
- **WHOIS & RDAP Registry:** Queries domain and IP ownership metadata via ICANN RDAP (Registration Data Access Protocol) for registrar, registration date, expiration date, and active status codes.
- **IP Geolocation & ASN Lookup:** Identifies geographic coordinates, country, city, ISP carrier, and Autonomous System Numbers (ASN) with automated private RFC1918/loopback classification.

### 2. 🔒 Security & Encoding
- **JWT Token Inspector:** Decodes JSON Web Tokens (RFC 7519), validates standard claims (`sub`, `iss`, `aud`, `exp`, `nbf`, `iat`), provides real-time expiration countdowns, and verifies cryptographic signatures with shared secrets.
- **Base64 Encoder / Decoder:** Bi-directional conversions for standard and URL-safe Base64 (RFC 4648) with automatic padding recovery and hex inspection.
- **URL Component Encoder / Decoder:** RFC 3986 percent-encoding and query string parameter parser/builder.
- **Cryptographic Hash Engine:** Generates cryptographic digests (SHA-256, SHA-512, SHA-224, SHA-384, SHA-1, MD5) and keyed HMAC-SHA256 signatures.
- **High-Entropy Password & Secret Generator:** CSPRNG password generator with customizable character pools (uppercase, lowercase, numbers, symbols, ambiguous exclusion) and Shannon entropy bit strength scoring.

### 3. 🔄 Data & Format Converters
- **JSON ↔ YAML Converter:** Bi-directional transformations preserving types, unicode, and structure.
- **JSON ↔ CSV Converter:** Tabular serialization converting JSON arrays of objects to CSV records and CSV tables to JSON lists.
- **JSON Validator & Beautifier / Minifier:** In-depth JSON syntax error diagnostic with line/column pointers, pretty-printing with custom indent, and whitespace minification.
- **Cron Syntax Parser:** Translates 5-field standard cron expressions into plain English schedules and calculates the next upcoming execution timestamps (UTC).
- **Markdown Previewer:** Real-time Markdown parser generating sanitized HTML with syntax-highlighted code blocks.

### 4. 🩺 System Diagnostics
- **HTTP Header Inspector:** Probes target URLs via HTTP HEAD/GET, measures round-trip response latency (ms), and grades security posture across critical headers (`Strict-Transport-Security`, `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`).
- **SSL / TLS Certificate Checker:** Direct TLS socket handshake inspector extracting X.509 validity dates, days until expiry, certificate issuer, TLS protocol version, cipher suite, and Subject Alternative Names (SANs).
- **UUID & Identifier Generator:** Generates UUIDv4 (random CSPRNG), UUIDv1 (time/MAC), and UUIDv5 (name-based) with case and hyphen formatting options.

---

## 💻 Tech Stack & Architecture

The project features a **Dual-Stack Architecture**:

| Layer | Technologies |
| :--- | :--- |
| **Backend & REST API** | Python 3.11+, FastAPI, Uvicorn, Pydantic V2 |
| **Interactive Dashboard** | Streamlit, Pandas, Plotly |
| **Frontend Web App** | Vue 3, Vite, TypeScript, UnoCSS, Web Workers (it-tools) |
| **Networking & Protocols** | dnspython, Requests, SSL, Sockets, IPAddress |
| **Cryptographic Primitives**| PyJWT, Cryptography, Hashlib, Secrets (CSPRNG) |
| **Container & Deployment** | Docker (Multi-Stage), Nginx, Netlify, Vercel |

```
                              ┌───────────────────────────────────────────┐
                              │     Cloud Utility Tools Web Platform      │
                              └─────────────────────┬─────────────────────┘
                                                    │
                ┌───────────────────────────────────┴───────────────────────────────────┐
                ▼                                                                       ▼
   ┌───────────────────────────┐                                           ┌───────────────────────────┐
   │    Vue 3 / Vite Portal    │                                           │  Python / Streamlit Suite │
   │ (TypeScript, UnoCSS, SPA) │                                           │   (Interactive Dashboards)│
   └────────────┬──────────────┘                                           └────────────┬──────────────┘
                │                                                                       │
                │                                                                       ▼
                │                                                          ┌───────────────────────────┐
                │                                                          │    FastAPI REST Engine    │
                │                                                          │ (OpenAPI /docs, Headless) │
                │                                                          └────────────┬──────────────┘
                │                                                                       │
                └───────────────────────────────────┬───────────────────────────────────┘
                                                    ▼
                       ┌────────────────────────────────────────────────────────┐
                       │               Modular Engine Micro-Tools               │
                       ├────────────────────┬───────────────────────────────────┤
                       │ tools/networking   │ DNS, CIDR, WHOIS, IP Geolocation  │
                       │ tools/security     │ JWT, Base64, Hashes, Passwords    │
                       │ tools/converters   │ JSON, YAML, CSV, Cron Parser      │
                       │ tools/diagnostics  │ HTTP Headers, SSL/TLS, UUIDs      │
                       └────────────────────────────────────────────────────────┘
```

---

## 📂 Directory Tree

```text
Cloud-Utility-Tools-Website/
├── components/                      # Reusable dashboard UI widgets & cards
│   ├── __init__.py
│   └── ui_cards.py                  # HTML status badges & metric components
│
├── static/                          # Static branding, CSS styling & assets
│   ├── logo.svg                     # Vector brand logo
│   └── style.css                    # Modern dark-mode stylesheet
│
├── templates/                       # Exportable report templates & schemas
│   ├── cidr_planning_template.csv   # VPC subnet capacity planning template
│   ├── dns_report.md                # Markdown template for DNS audits
│   └── ssl_audit_report.json        # Structured SSL health audit template
│
├── tools/                           # Modular Python utility micro-engines
│   ├── __init__.py                  # Package exports
│   ├── converters.py                # JSON, YAML, CSV, Cron, Markdown
│   ├── diagnostics.py               # HTTP headers, SSL certificates, UUIDs
│   ├── networking.py                # DNS resolution, CIDR calculator, RDAP, GeoIP
│   └── security.py                  # JWT decoder, Base64, URL, Hashes, Passwords
│
├── src/                             # Upstream Vue 3 / Vite single-page application
│   ├── assets/                      # Frontend icons and stylesheets
│   ├── components/                  # Vue UI components
│   ├── layouts/                     # Responsive layout shells
│   ├── modules/                     # Web tool modules
│   ├── pages/                       # SPA routing views
│   ├── tools/                       # Client-side JavaScript tool engines
│   └── main.ts                      # Vite entrypoint
│
├── app.py                           # Dual-mode Streamlit dashboard & CLI launcher
├── main.py                          # FastAPI REST service & CLI diagnostic audit
├── test_tools.py                    # Pytest test suite (100% pass rate)
├── requirements.txt                 # Pinned Python backend dependencies
├── package.json                     # Frontend Node dependencies (Vue 3 / Vite)
├── vite.config.ts                   # Vite build configuration
├── Dockerfile                       # Multi-stage production container
└── IT_TOOLS_GUIDE.md                # Original documentation reference
```

---

## ⚡ Quickstart Guide

### Option A: Python Suite (FastAPI & Streamlit)

#### 1. Virtual Environment Setup
```bash
# Clone the repository
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/Cloud-Utility-Tools-Website

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / macOS:
# source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run Development Servers
```bash
# Terminal 1: Launch Interactive Visual Streamlit Dashboard
streamlit run app.py

# Terminal 2: Launch FastAPI REST Service (with Swagger UI at http://127.0.0.1:8000/docs)
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Or run terminal diagnostic benchmark:
python main.py --audit
```

#### 4. Run Automated Test Suite
```bash
pytest test_tools.py -v
```

---

### Option B: Node.js / Vue 3 Frontend (it-tools Web Suite)

```bash
# 1. Install Node dependencies (Node 18+)
pnpm install  # or npm install

# 2. Run local development server
npm run dev

# 3. Build optimized production bundle
npm run build
```

---

### Option C: Containerization with Docker

```bash
# 1. Build Docker image
docker build -t cloud-utility-tools .

# 2. Run container
docker run -d -p 8080:80 --name cloud-tools cloud-utility-tools

# Access application at http://localhost:8080
```

---

## 🔌 REST API Documentation

When running `uvicorn main:app`, explore interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

### Primary Endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status check |
| `POST` | `/api/dns` | Resolve DNS records (`A`, `AAAA`, `MX`, `TXT`, etc.) |
| `POST` | `/api/cidr` | Calculate subnet boundaries and host counts |
| `POST` | `/api/whois` | Query RDAP domain registration metadata |
| `POST` | `/api/ip-geo` | IP geolocation and ASN carrier details |
| `POST` | `/api/jwt` | Decode and validate JSON Web Token claims |
| `POST` | `/api/base64/encode` | Encode text to Standard or URL-safe Base64 |
| `POST` | `/api/base64/decode` | Decode Base64 string to plaintext |
| `POST` | `/api/hash` | Compute SHA-256, SHA-512, MD5, and HMAC |
| `POST` | `/api/password` | Generate CSPRNG high-entropy passwords |
| `POST` | `/api/convert/json-yaml` | Convert JSON payload to YAML |
| `POST` | `/api/convert/yaml-json` | Convert YAML payload to JSON |
| `POST` | `/api/convert/json-csv` | Convert JSON list of objects to CSV |
| `POST` | `/api/cron` | Parse cron syntax and compute next trigger dates |
| `POST` | `/api/diagnostics/headers` | Probe HTTP response headers and grade security |
| `POST` | `/api/diagnostics/ssl` | Connect to TLS socket and audit SSL certificate |
| `GET` | `/api/uuid` | Generate batch UUIDv1, UUIDv4, or UUIDv5 |

---

## 👤 Author

**Rithikesh S**  
- GitHub: [@rithikesh18-rk](https://github.com/rithikesh18-rk)
