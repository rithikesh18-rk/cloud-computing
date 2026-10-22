# Cloud Website Uptime & Endpoint Reliability Monitor

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite3](https://img.shields.io/badge/SQLite-ACID_Engine-003B57.svg?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Dark_Analytics-3F4F75.svg?style=flat&logo=plotly&logoColor=white)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, distributed website health-checker, latency observability engine, and SLA compliance monitoring hub. Features automated multi-endpoint periodic HTTP/HTTPS probing, SSL/TLS certificate expiry tracking, incident state machine lifecycles, and multi-channel alerting hooks.

---

## 📌 Problem Statement

In distributed cloud architectures and multi-region microservices, unnoticed downtime, silent SSL/TLS certificate expirations, and subtle network latency degradations severely compromise user experience, breach Service Level Agreements (SLAs), and cause unrecoverable brand damage.

Traditional monitoring tools are frequently heavyweight, closed-source, or overly complex for focused endpoint reliability assurance. The **Cloud Website Uptime & Endpoint Reliability Monitor** provides a self-hosted, lightweight, and fault-tolerant observability stack that proactively polls service endpoints, tracks TLS certificate validity, logs incident timelines, calculates exact uptime compliance percentages, and dispatches real-time incident alerts.

---

## ✨ Core Features

- **Multi-Endpoint Health Polling:** Performs synchronous or continuous asynchronous HTTP/HTTPS sweeps across configured services, measuring HTTP status codes, redirection hops, and precise round-trip latency in milliseconds.
- **SSL/TLS Certificate Validity & Expiration Watchdog:** Connects directly via TLS sockets to inspect peer certificates, calculate days remaining until expiration, extract issuer Certificate Authorities (CAs), and raise warnings for certificates expiring within 30 days.
- **Automated Incident State Machine:** Tracks endpoint transitions (`OPERATIONAL` $\leftrightarrow$ `DOWN`). Automatically logs incident start times, calculates outage durations upon recovery, and attributes root causes.
- **SLA Availability Calculations:** Computes rolling 24-hour, 7-day, and 30-day SLA availability percentages (`healthy_checks / total_checks * 100`) and fleet average latency metrics.
- **Multi-Channel Alert Dispatches:** Triggers formatted incident notifications and recovery payloads to Slack incoming webhooks, Discord, PagerDuty, or SMTP email logs upon state transitions.
- **Dual-Mode Interactive Dashboard & CLI Auditor:**
  - **Streamlit Web UI:** Real-time KPI metric cards, status badges (🟢 Operational, 🟡 Degraded, 🔴 Outage), interactive Plotly latency curve graphs, SSL watchdog tables, incident timelines, and one-click manual probe triggers.
  - **CLI Auditor:** Styled ASCII audit report for terminal environments, CI/CD pipelines, and headless server environments.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Language & Runtimes** | Python 3.11+, Node.js (Full-stack Kuma core), PowerShell / Bash |
| **Network & SSL Engines** | `urllib`, `requests`, `ssl`, `socket`, `cryptography`, `urllib3` |
| **Storage & Persistence** | SQLite 3 (`uptime_monitor.db`), JSON (`endpoints.json`), Structured log files (`logs/`) |
| **Visual Dashboard** | Streamlit, Plotly Express, Pandas |
| **Alert Integrations** | Webhooks (Slack / Discord / PagerDuty), Structured alert dispatcher |
| **Packaging & Deployment** | Docker Compose, Systemd daemon, Cross-platform CLI runner |

---

## 🏛️ System Architecture

```text
  ┌─────────────────────────────────────────────────────────────┐
  │                      endpoints.json                         │
  │     (Target URLs, Intervals, Timeouts, Expected Status)     │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │               checker.py (Core Polling Engine)              │
  │  ├── HTTP/HTTPS Round-Trip Probe (Status & Latency ms)      │
  │  ├── Peer TLS Certificate Inspector (Days to Expiry & CA)   │
  │  ├── Incident State Machine (OPERATIONAL ↔ DOWN)            │
  │  └── Alert Dispatcher (Slack / Webhooks / Incident Logs)    │
  └──────────────┬──────────────────────────────┬───────────────┘
                 │                              │
                 ▼                              ▼
  ┌──────────────────────────────┐  ┌───────────────────────────┐
  │  uptime_monitor.db (SQLite)  │  │   logs/ Directory         │
  │  - endpoints                 │  │   - uptime.log (Audits)   │
  │  - health_checks             │  │   - alerts.log (Dispatches│
  │  - incidents                 │  └───────────────────────────┘
  │  - alerts                    │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │               app.py (Visualization & Reporting)            │
  │  ├── Streamlit Dark Dashboard (Real-time Fleet Observability)│
  │  ├── Plotly Interactive Latency Curves                      │
  │  ├── SSL Expiry Watchdog & Timeline Grid                    │
  │  └── Terminal CLI Audit Mode (CI/CD Pipeline Validation)    │
  └─────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```text
Website-Uptime-Monitoring/
├── app.py                      # Dual-mode visual dashboard & terminal auditor
├── checker.py                  # Core health polling engine, SSL tracker & incident manager
├── endpoints.json              # Configurable endpoint target registry
├── requirements.txt            # Python dependencies (Streamlit, Plotly, Pandas, etc.)
├── uptime_monitor.db           # SQLite database storing health checks, incidents & alerts
├── UPTIME_KUMA_GUIDE.md        # Reference guide for full-stack Node.js engine
├── UPSTREAM_AGENTS.md          # Upstream agent policy reference
├── logs/
│   ├── alerts.log              # Dispatched incident & recovery alert payloads
│   └── uptime.log              # Raw chronological probe telemetry logs
├── db/                         # Node.js backend SQLite migrations & knex schemas
├── docker/                     # Container runtime scripts & Dockerfile configurations
├── server/                     # Full-stack Uptime Kuma backend socket & REST services
├── src/                        # Vue 3 / Vite frontend application source code
└── index.html                  # HTML5 entrypoint for full-stack web UI
```

---

## 🚀 Quickstart Guide

### 1. Virtual Environment Setup

```bash
# Navigate to the module directory
cd Website-Uptime-Monitoring

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Polling & Health-Check Engine

```bash
# Run a single audit sweep across all endpoints
python checker.py --once

# Or launch continuous background polling (e.g. every 30 seconds):
python checker.py --interval 30

# Print rolling 24-hour SLA availability summary:
python checker.py --summary
```

### 4. Launch Interactive Status UI

```bash
# Launch the rich Streamlit dashboard
streamlit run app.py

# Or run terminal CLI mode:
python app.py
```

---

## ⚙️ Configuration (`endpoints.json`)

Customize targets to monitor in `endpoints.json`:

```json
[
  {
    "id": 1,
    "name": "Production API Gateway",
    "url": "https://api.github.com",
    "check_interval": 30,
    "timeout": 5,
    "expected_status": 200,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Cloudflare Edge DNS",
    "url": "https://1.1.1.1",
    "check_interval": 60,
    "timeout": 5,
    "expected_status": 200,
    "is_active": true
  }
]
```

---

## 📊 Database Schema

The system maintains four relational SQLite tables:

1. **`endpoints`**: Registered target services, URLs, timeout limits, check intervals, and active status.
2. **`health_checks`**: Time-series health checks containing HTTP response codes, response latency (ms), operational state (`OPERATIONAL`, `DEGRADED`, `DOWN`), SSL days remaining, and error details.
3. **`incidents`**: Outage event records tracking `started_at`, `resolved_at`, total downtime duration (seconds), and root cause attribution.
4. **`alerts`**: Chronological log of incident and recovery notification dispatches with target channels.

---

## 👤 Author

**Rithikesh S**  
- GitHub: [@rithikesh18-rk](https://github.com/rithikesh18-rk)
- Cloud Computing Project Series
