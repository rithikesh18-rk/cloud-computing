# Real-Time Internet Speed & Network Reliability Monitor

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20.0-3F4F75.svg?style=flat&logo=plotly&logoColor=white)](https://plotly.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg?style=flat)]()

An automated network telemetry and reliability monitoring system tracking latency, jitter, download/upload bandwidth, packet loss, and ISP Service Level Agreement (SLA) compliance.

---

## 📌 Problem Statement

Broadband subscribers, remote engineers, and cloud infrastructure operations frequently suffer from **network performance degradation**, **silent ISP bandwidth throttling during peak hours**, and **micro-outages**. Without continuous historical telemetry, end users and enterprises lack quantifiable evidence to hold Internet Service Providers (ISPs) accountable to their advertised Service Level Agreements (SLAs) or diagnose internal network bottlenecks.

This project bridges that gap by running an autonomous network telemetry daemon and providing an interactive visual dashboard that captures, logs, analyzes, and visualizes network health trends over time.

---

## 🚀 Key Capabilities

- **Automated Periodic Telemetry:** Continuous benchmarking of download throughput, upload bandwidth, handshake latency (ping), jitter variation, and packet loss.
- **ISP SLA Compliance Engine:** Real-time evaluation against configurable SLA thresholds (e.g., minimum 100 Mbps download, 25 Mbps upload, maximum 35 ms ping, 10 ms jitter).
- **Silent Throttling Detection:** Hourly diurnal performance analysis identifying peak congestion windows where ISPs systematically throttle bandwidth.
- **Dual Storage Persistence:** Stores time-series metrics in both indexed SQLite (`telemetry.db`) and portable CSV (`telemetry.csv`) formats.
- **Alert Triggers & Incident Logging:** Automated detection and categorization of network drops, packet loss spikes, and SLA violations.
- **Interactive Visual Dashboard:** Full-featured Streamlit UI featuring live metric KPI dials, Plotly time-series charts, throughput distribution histograms, ping latency boxplots, and one-click live benchmarking.
- **Lightweight HTML5 Speedtest Engine:** Embedded client-side browser testing suite powered by pure JavaScript XMLHttpRequest and Web Workers for zero-plugin local and remote speed measurements.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ / 3.13 | Core telemetry daemon, network sockets, benchmarking |
| **Telemetry Engine** | Socket Handshake / Speedtest API / CDN chunking | Latency, jitter, packet loss, and throughput measurement |
| **Storage & Data** | SQLite3 & Pandas | ACID time-series metrics database & analytical processing |
| **Interactive UI** | Streamlit & Plotly Express / Graph Objects | Dark-mode interactive web dashboard & real-time telemetry charts |
| **Web Speedtest** | HTML5 / Vanilla JavaScript / Web Workers | Client-side in-browser bandwidth and stability testing |
| **Containerization** | Docker & Alpine Linux | Multi-stage Docker deployment specs for containerized nodes |

---

## 📂 Folder Structure

```text
Internet-Speed-Monitoring/
│
├── monitor.py                 # Core telemetry engine, benchmark tester & daemon
├── app.py                     # Dual-mode Streamlit dashboard & CLI audit runner
├── requirements.txt           # Python analytics & visualization dependencies
├── telemetry.db               # SQLite database storing historical time-series metrics
├── telemetry.csv              # CSV audit log for export and external ingestion
│
├── index.html                 # LibreSpeed HTML5 speedtest web interface
├── index-modern.html          # Modern speedtest UI layout
├── index-classic.html         # Classic responsive layout
├── stability.html             # Extended connection stability and packet loss tester
├── speedtest.js               # Client-side speed test orchestration engine
├── speedtest_worker.js        # Web Worker handling async XHR download/upload streams
├── stability_worker.js        # Web Worker for continuous ping and latency profiling
│
├── backend/                   # Multi-language backend telemetry endpoints (PHP, Node, Go)
│   ├── empty.php              # Fast empty response endpoint for latency testing
│   ├── garbage.php            # Chunk generator for download throughput benchmarking
│   └── getIP.php              # Client IP, ISP identification, and geolocation
│
├── docker/                    # Docker container deployment scripts and Nginx configs
├── Dockerfile                 # Multi-stage production container image
├── Dockerfile.alpine          # Ultra-lightweight Alpine container spec
├── server-list.json           # Configurable test server list
├── settings.json              # Client-side visual test settings
│
├── LIBRESPEED_GUIDE.md        # Original LibreSpeed engine documentation
└── README.md                  # Project documentation & quickstart playbook
```

---

## ⚡ Quickstart Guide

### 1. Virtual Environment Setup

Create and activate an isolated Python virtual environment:

```bash
# Windows (PowerShell / Command Prompt)
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

### 3. Run Benchmark / Start Monitor Daemon

Run a single network benchmark audit from the command line:

```bash
python monitor.py
```

*Example Output:*
```text
======================================================================
  INTERNET SPEED & NETWORK RELIABILITY TELEMETRY BENCHMARK
======================================================================
Timestamp:       2026-10-22 10:29:22 UTC
Status:          ONLINE
ISP Provider:    Broadband Provider
Gateway Server:  Cloudflare Speed CDN
----------------------------------------------------------------------
Download Speed:    128.45 Mbps  (SLA: >= 100.0 Mbps)
Upload Speed:       38.20 Mbps  (SLA: >= 25.0 Mbps)
Ping / Latency:      9.09 ms    (SLA: <= 35.0 ms)
Jitter:              3.69 ms    (SLA: <= 10.0 ms)
Packet Loss:         0.00 %     (SLA: <= 1.0 %)
----------------------------------------------------------------------
SLA Compliance:  PASSED - SLA Compliant
======================================================================
Record stored in SQLite [telemetry.db] and CSV [telemetry.csv].
```

To run the automated background telemetry daemon (polling every 5 minutes):

```bash
python monitor.py --daemon --interval 300
```

To seed 7 days of realistic historical timeseries data for immediate dashboard exploration:

```bash
python monitor.py --seed
```

### 4. Launch the Interactive Dashboard

Launch the Streamlit visualization portal:

```bash
streamlit run app.py
```

Or run the CLI audit summary:

```bash
python app.py
```

The interactive dashboard will open at `http://localhost:8501`, featuring:
- **Live Metric Dials:** Real-time download, upload, ping, jitter, packet loss, and SLA health percentage.
- **SLA Sliders:** Interactive sidebar controls to test different service tiers and contract thresholds.
- **Throughput & Latency Timeseries:** Interactive Plotly curves with SLA threshold lines.
- **Diurnal Throttling Heatmap:** Hourly distribution uncovering ISP evening peak slowdowns.
- **Incident Log Table:** Detailed log of all historical SLA violations and outages with CSV export.

---

## 🌐 HTML5 Speedtest Web Portal

To test in-browser without Python, open `index.html` directly or host the directory on any web server (Apache, Nginx, or Docker):

```bash
docker build -t internet-speed-monitor .
docker run -d -p 80:80 internet-speed-monitor
```

---

## 📄 License & Attribution

This project incorporates the open-source LibreSpeed HTML5 test engine under the GNU Lesser General Public License (LGPL-3.0) and extends it with autonomous Python telemetry daemons, SQLite storage, and Streamlit analytics.
