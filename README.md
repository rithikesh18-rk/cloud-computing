# Cloud Computing Repository

A collection of cloud architecture implementations, resource managers, and distributed systems.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000.svg?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1.0-EB6424.svg?style=flat&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/GitHub_Actions-Passing-2088FF.svg?style=flat&logo=githubactions&logoColor=white)](https://github.com/rithikesh18-rk/cloud-computing/actions)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cloudaqipredictor-mxappeflcb2uurjcacex2uq.streamlit.app)

This repository contains production-ready full-stack and cloud-native machine learning projects developed for the **Cloud Computing** subject. Each project is organized into its own self-contained directory with its complete source code, configuration files, automated tests, dependencies, and documentation.

---

## 🌐 Live Deployments & Application Access

| Project / Module | Description | Core Stack | Status |
| :--- | :--- | :--- | :--- |
| **[Cloud-Based AQI Predictor](./cloud-aqi-predictor)** | Real-time Air Quality Index prediction and official EPA health advisories with XGBoost Regressor | Python 3.11, XGBoost, FastAPI, Streamlit, Docker | Complete |
| **[Employee Management System](./Employee-Management-System)** | Full-stack HR portal managing employee lifecycles, departments, and leave workflows | Python, Flask, SQLAlchemy, MySQL, Render | Complete |
| **[Attendance Management System](./Attendance-Management-System)** | Multi-role academic attendance system with short-attendance alerting and PDF/Excel reporting | Python, Flask, SQLite / MySQL, Bootstrap 5, Chart.js | Complete |
| **[Multi-Warehouse Inventory System](./Cloud-Based-Inventory-Management-System)** | Enterprise multi-warehouse inventory control with ACID transactions & ML demand forecasting | Python, Streamlit, MySQL DBaaS, SQLAlchemy, Scikit-Learn | Complete |
| **[CloudPulse AI](./cloudpulse-ai)** | Predictive cloud workload forecasting and autoscaling benchmark simulation lab | Python 3.11, FastAPI, Random Forest, React 18, Vite, TypeScript | Complete |
| [Cloud-Cost-Optimization](./Cloud-Cost-Optimization) | Automated cloud resource monitoring, rightsizing, idle-instance detection, and cost-allocation analyzer | Python, Cloud APIs, Analytics / Dashboard | Complete |
| [Internet-Speed-Monitoring](./Internet-Speed-Monitoring) | Automated network telemetry tool tracking latency, jitter, download/upload bandwidth, and ISP SLA compliance | Python, Speedtest CLI / Ping APIs, SQLite / CSV, Dashboard | Complete |
| [Website-Uptime-Monitoring](./Website-Uptime-Monitoring) | Automated endpoint health-checker tracking HTTP status codes, SSL expiry, latency, and incident alerting | Python, Requests / Asyncio, SQLite / Logs, Dashboard | Complete |
| [Cloud-Password-Manager](./Cloud-Password-Manager) | Zero-knowledge encrypted cloud credential vault featuring client-side AES-GCM encryption and PBKDF2/Argon2 key derivation | Python, Cryptography (AES-256), SQLite / Cloud DB, Streamlit / FastAPI | Complete |
| [Cloud-Utility-Tools-Website](./Cloud-Utility-Tools-Website) | Unified cloud-native web suite offering essential developer & sysadmin utilities (DNS lookup, CIDR calculator, Base64/JWT decoder, file format converter, hash generator) | Python / FastAPI / Streamlit or React / Tailwind, Cloud APIs | Complete |

---

## 📁 Projects Overview

### 1. 🌫️ Cloud-Based Air Quality Index (AQI) Predictor & Forecast

- **Live Demo:** [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cloudaqipredictor-mxappeflcb2uurjcacex2uq.streamlit.app)
- **Direct URL:** [https://cloudaqipredictor-mxappeflcb2uurjcacex2uq.streamlit.app](https://cloudaqipredictor-mxappeflcb2uurjcacex2uq.streamlit.app)
- **Description:** A production-grade Machine Learning cloud application for real-time Air Quality Index prediction and official EPA-standard health advisories. Evaluates multi-pollutant metrics (PM2.5, PM10, NO2, SO2, CO) and weather conditions (Temperature, Humidity) with an XGBoost Regressor model ($R^2 = 0.9991$).
- **Architecture Highlights:**
  - **Dual-Mode ML Engine:** Runs standalone in-process cached inference on Streamlit Community Cloud and interfaces with FastAPI REST endpoints in distributed environments.
  - **Interactive Visualizations:** Plotly dynamic gauge dials and pollutant concentration breakdown charts against standard baseline thresholds.
  - **DevOps:** Multi-stage `Dockerfile`, GitHub Actions CI/CD workflow, and automated Pytest test suite.
- **Technologies Used:** Python 3.11, XGBoost, Scikit-Learn, FastAPI, Streamlit, Plotly, Docker, GitHub Actions.
- **Subdirectory:** [`cloud-aqi-predictor/`](./cloud-aqi-predictor/)

---

### 2. 👥 Employee Management System

- **Live Demo:** 🚀 **[https://employee-management-system-bv3y.onrender.com/](https://employee-management-system-bv3y.onrender.com/)**
- **Description:** A comprehensive Flask-based Human Resource (HR) management platform designed to manage employee lifecycle records, corporate departmental hierarchies, daily attendance logs, and leave approval workflows. Features secure admin authentication, search & filtering, analytics dashboards, and automated cloud hosting configuration on Render.
- **Technologies Used:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, WTForms, PyMySQL, Cryptography, Chart.js, Render (`render.yaml`).
- **Subdirectory:** [`Employee-Management-System/`](./Employee-Management-System/)

---

### 3. 🎓 Attendance Management System

- **Live Demo:** 🚀 [https://attendance-management-system-1-3fey.onrender.com/](https://attendance-management-system-1-3fey.onrender.com/)
- **Description:** A full-stack, responsive academic attendance management platform built for educational institutions. Features multi-role authentication (Admin, Faculty, Student), dynamic institutional branding, class attendance marking with bulk toggles, attendance percentage calculations with shortage (< 75%) alerts, Chart.js analytics, and downloadable PDF & Excel export capabilities.
- **Technologies Used:** Python, Flask, Flask-SQLAlchemy, PyMySQL / SQLite, Bootstrap 5, Chart.js, ReportLab (PDF), OpenPyXL (Excel).
- **Subdirectory:** [`Attendance-Management-System/`](./Attendance-Management-System/)

---

### 4. 📦 Cloud-Based Multi-Warehouse Inventory Management System

- **Live Demo:** 🚀 [Cloud Inventory Orchestrator](https://rk-inventory-cloud.streamlit.app/)
- **Description:** An enterprise-grade, cloud-native inventory control and warehouse orchestration platform targeting Streamlit Community Cloud and managed MySQL DBaaS. Features dynamic multi-warehouse balance monitoring, real-time critical low-stock alerting, explicit ACID transaction handlers with row-level locking (`SELECT ... FOR UPDATE`), atomic inter-warehouse transfers, and an ML demand forecasting engine with linear burn rate estimation and 14-day stock depletion projections.
- **Architecture Highlights:**
  - **ACID Transaction Handlers:** Thread-safe connection pooling, row-level locking, and exponential backoff retry decorators for deadlock resilience.
  - **Machine Learning Forecasting:** Linear trend daily burn rate estimation, Estimated Days Until Stockout (EDUS), and dynamic safety replenishment recommendations.
  - **Cloud-Ready DBaaS Schema:** Normalized InnoDB schema (5 tables, 3 analytical SQL views, foreign key constraints, check constraints).
- **Technologies Used:** Python 3.11, Streamlit 1.38, SQLAlchemy 2.0, PyMySQL, Scikit-Learn, Plotly, MySQL 8.0+.
- **Subdirectory:** [`Cloud-Based-Inventory-Management-System/`](./Cloud-Based-Inventory-Management-System/)

---

### 5. ⚡ CloudPulse AI — Predictive Cloud Workload Forecasting & Resource Optimization System

- **Dashboard:** 🚀 [Local CloudPulse UI](http://127.0.0.1:5173/) | [FastAPI Swagger Docs](http://127.0.0.1:8000/docs)
- **Description:** An AI-powered Cloud Infrastructure Management and Simulation System. CloudPulse AI addresses the challenges of dynamic cloud resource allocation by pairing a multi-step forward Random Forest workload forecaster with a discrete-event cloud cluster simulator. It benchmarks reactive threshold auto-scaling against predictive auto-scaling to eliminate latency spikes, minimize SLA violations, and prevent over-provisioning expenditure.
- **Architecture Highlights:**
  - **Workload Forecasting Engine:** 14-day 5-minute interval telemetry generator with diurnal rhythms and Poisson spikes; lag features ($t-1, t-2, t-3, t-6$), rolling metrics (3 & 6 steps), cyclical harmonic encodings, and strictly chronological 80/20 train/test splits. Multi-step recursive forecasting across 3, 6, and 12-step horizons ($R^2 \ge 0.95$).
  - **Discrete Cloud Simulator:** Full virtual instance lifecycle (`ACTIVE`, `PROVISIONING`, `TERMINATING`), dynamic queueing latency penalty $L_t = L_{base} \cdot \max\left(1, \left(\frac{\lambda_t}{C_t}\right)^2\right)$, SLA violation threshold tracking ($>200\text{ms}$), and real-time node-hour cost model.
  - **7-View Modern Dashboard:** Overview, Workload Analytics, Multi-Step Predictions, Resource Optimization, Simulation Lab, Experiment Reports (with CSV export), and System Settings built with React 18, Vite, TypeScript, Tailwind CSS, and Recharts.
- **Technologies Used:** Python 3.11, FastAPI, Pydantic v2, Scikit-Learn, Pandas, NumPy, SQLAlchemy, React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons, Recharts.
- **Subdirectory:** [`cloudpulse-ai/`](./cloudpulse-ai/)

---

### 6. 💰 Cloud Cost Optimization & Resource Governor

- **Dashboard:** 🚀 [Local Cost Governor UI](http://localhost:8501) | [Next.js Full-Stack Portal](http://localhost:3000)
- **Description:** An enterprise multi-cloud resource governor and cost observability hub. Monitors compute utilization (CPU, memory, storage IOPS) across AWS, GCP, and Azure, detects daily/monthly billing spikes using statistical rolling Z-score anomalies, and automatically generates rightsizing and idle-instance shutdown recommendations with projected annual OpEx savings.
- **Architecture Highlights:**
  - **Utilization Telemetry Engine:** Continuous tracking of compute utilization, memory pressure, and I/O profiles across heterogeneous cloud fleets.
  - **Billing Anomaly Detection:** Rolling baseline 3-sigma statistical anomaly detector identifying silent billing spikes and attributing root causes.
  - **Automated Rightsizing & Governor:** Enforces idle resource shutdown (`TAG_AND_SHUTDOWN`) and instance downscaling (`RIGHTSIZE_DOWNGRADE`).
  - **Dual-Stack Runtime:** Standalone Python/Streamlit analytics dashboard + decoupled Go Gin REST API & Next.js 15 web portal with TimescaleDB & Redis.
- **Technologies Used:** Python 3.11, Streamlit, Plotly, Pandas, NumPy, Go 1.21+, Next.js 15, React 19, TypeScript, Tailwind CSS, PostgreSQL / TimescaleDB, Docker Compose.
- **Subdirectory:** [`Cloud-Cost-Optimization/`](./Cloud-Cost-Optimization/)

---

### 7. 📶 Real-Time Internet Speed & Network Reliability Monitor

- **Dashboard:** 🚀 [Local Telemetry UI](http://localhost:8501) | [HTML5 Speedtest Engine](./Internet-Speed-Monitoring/index.html)
- **Description:** An automated network telemetry and reliability monitoring system tracking latency, jitter, download/upload throughput, packet loss, and ISP Service Level Agreement (SLA) compliance. Identifies silent ISP peak-hour bandwidth throttling, micro-outages, and logs time-series telemetry into SQLite and CSV stores.
- **Architecture Highlights:**
  - **Automated Network Telemetry:** Dual-engine benchmarking using socket handshakes, CDN chunk testing, and speedtest APIs for robust, resilient data collection.
  - **ISP SLA Compliance Engine:** Real-time violation detection against configurable download, upload, ping, jitter, and packet loss targets.
  - **Diurnal Throttling Analytics:** Identifies systematic evening peak congestion windows and recurring bandwidth throttling.
  - **Interactive Streamlit Portal:** Real-time KPI dials, Plotly trend curves, latency distribution histograms, and instant on-demand speedtest execution.
  - **Client-Side HTML5 Suite:** Embedded zero-plugin web speedtest powered by pure JavaScript and Web Workers.
- **Technologies Used:** Python 3.11+, Streamlit, Plotly, SQLite3, Pandas, HTML5, Web Workers, Docker.
- **Subdirectory:** [`Internet-Speed-Monitoring/`](./Internet-Speed-Monitoring/)

---

### 8. 🌐 Cloud Website Uptime & Endpoint Reliability Monitor

- **Dashboard:** 🚀 [Local Streamlit UI](http://localhost:8501) | [CLI Health Auditor](file:///./Website-Uptime-Monitoring/app.py)
- **Description:** An enterprise-grade, distributed website health-checker, latency observability engine, and SLA compliance monitoring hub. Features automated multi-endpoint periodic HTTP/HTTPS probing, SSL/TLS certificate expiry tracking, incident state machine lifecycles, and multi-channel alerting hooks.
- **Architecture Highlights:**
  - **Multi-Endpoint Health Poller:** Continuous HTTP/HTTPS availability checks, redirection handling, and precision response latency measurement.
  - **SSL/TLS Expiration Watchdog:** Direct TLS socket handshake verification, extraction of certificate validity, and automated expiration warnings (< 30 days).
  - **Incident State Machine:** Tracks endpoint transitions (`OPERATIONAL` ↔ `DOWN`), measures exact downtime duration, and logs root causes.
  - **SLA Availability Engine:** Computes rolling 24-hour, 7-day, and 30-day SLA availability compliance percentages and fleet average latencies.
  - **Dual-Stack Runtime:** Standalone Python/Streamlit analytics dashboard & CLI auditor + full-stack Node.js engine with SQLite/knex persistence.
- **Technologies Used:** Python 3.11, Streamlit, Plotly, Pandas, SQLite 3, Cryptography, Requests / Urllib, Node.js.
- **Subdirectory:** [`Website-Uptime-Monitoring/`](./Website-Uptime-Monitoring/)

---

### 9. 🔐 Zero-Knowledge Cloud Password Manager & Vault

- **Dashboard:** 🚀 [Local Streamlit UI](http://localhost:8501) | [Interactive CLI Auditor](file:///./Cloud-Password-Manager/main.py)
- **Description:** An enterprise-grade, zero-knowledge encrypted credential vault and password manager. Eliminates cloud credential breach risks and third-party host snooping by generating 256-bit AES encryption keys strictly in client memory using Argon2id/PBKDF2 and storing only AES-256-GCM ciphertext and nonces.
- **Architecture Highlights:**
  - **Zero-Knowledge Architecture:** Master passwords never leave the client memory unhashed; cloud storage holds only authenticated ciphertext, unique 96-bit nonces, and independent auth verifiers.
  - **Cryptographic Primitives:** AES-256-GCM authenticated symmetric encryption paired with Argon2id / PBKDF2-HMAC-SHA256 (600,000 iterations).
  - **Credential Lifecycle:** Add, reveal, search, edit, and organize credentials with clipboard safety and in-memory decryption.
  - **Vulnerability & Entropy Auditor:** Live Shannon entropy calculation and vault analysis detecting weak or reused passwords.
  - **Dual-Stack Runtime:** Python Streamlit dark-mode dashboard & terminal console + Rust/Bitwarden upstream server compatibility.
- **Technologies Used:** Python 3.11+, Cryptography (AES-256-GCM), Argon2id, PBKDF2, Streamlit, SQLite 3, Rust / Bitwarden API.
- **Subdirectory:** [`Cloud-Password-Manager/`](./Cloud-Password-Manager/)

---

### 10. 🛠️ Cloud Utility Tools Suite & Web Platform

- **Dashboard:** 🚀 [Local Streamlit UI](http://localhost:8501) | [FastAPI Swagger Docs](http://127.0.0.1:8000/docs) | [Vue 3 Web Suite](./Cloud-Utility-Tools-Website/)
- **Description:** A unified, production-ready developer and sysadmin web suite offering essential cloud diagnostics, networking tools, cryptographic utilities, and format converters. Eliminates privacy exposure and reliance on ad-heavy third-party utility sites.
- **Architecture Highlights:**
  - **Networking & DNS Engine:** DNS record lookup (A, AAAA, MX, TXT, SOA), CIDR subnet boundary calculator with usable IP planning, RDAP WHOIS queries, and IP geolocation with RFC1918 classification.
  - **Security & Cryptography:** JWT claim inspector and expiration tracker, Base64/URL component encoding, cryptographic hash engine (SHA-256, SHA-512, MD5, HMAC), and CSPRNG high-entropy password generator.
  - **Data Serialization:** Bi-directional JSON ↔ YAML ↔ CSV transformations, pretty-printer / minifier, and 5-field cron syntax parser with upcoming execution timelines.
  - **System Diagnostics:** HTTP response header security posture auditor (HSTS, CSP, X-Frame-Options) and direct TLS socket SSL/TLS certificate validity inspector.
  - **Dual-Stack Platform:** Python (Streamlit visual UI + FastAPI REST service) and full-stack Vue 3 / Vite single-page application.
- **Technologies Used:** Python 3.11+, FastAPI, Uvicorn, Streamlit, dnspython, PyJWT, Cryptography, PyYAML, Requests, Vue 3, Vite, TypeScript, UnoCSS.
- **Subdirectory:** [`Cloud-Utility-Tools-Website/`](./Cloud-Utility-Tools-Website/)

---

## 🏗️ Repository Architecture

```text
cloud-computing/
│
├── .github/
│   └── workflows/
│       └── deploy.yml               # CI/CD Pipeline (Lint, Test, Docker Build)
│
├── Attendance-Management-System/     # Academic Attendance Management Application
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── static/
│   ├── templates/
│   ├── utils/
│   ├── app.py
│   └── README.md
│
├── Employee-Management-System/       # HR & Employee Management Portal
│   ├── app/
│   ├── Procfile
│   ├── render.yaml
│   ├── requirements.txt
│   ├── run.py
│   └── README.md
│
├── cloud-aqi-predictor/             # 🌟 Cloud-Based AQI Predictor & Forecast
│   ├── data/
│   │   └── aqi_dataset.csv          # 1500-sample training dataset
│   ├── frontend/
│   │   └── dashboard.py             # Streamlit visual analytics UI
│   ├── models/
│   │   └── aqi_model.joblib         # Serialized XGBoost Regressor model
│   ├── src/
│   │   ├── app.py                   # FastAPI REST application
│   │   ├── schemas.py               # Pydantic validation schemas
│   │   ├── train.py                 # ML training & dataset pipeline
│   │   └── utils.py                 # EPA classification & health advisories
│   ├── tests/
│   │   └── test_api.py              # Automated endpoint test suite
│   ├── Dockerfile                   # Multi-stage production container
│   ├── requirements.txt             # Project dependencies
│   └── README.md                    # Detailed subfolder documentation
│
├── Cloud-Based-Inventory-Management-System/ # 📦 Multi-Warehouse Inventory System
│   ├── .streamlit/
│   │   ├── config.toml              # Streamlit cloud UI & theme settings
│   │   └── secrets.toml.example     # Cloud DBaaS credentials template
│   ├── database/
│   │   ├── schema.sql               # MySQL 8.0 DDL (InnoDB, Views, Constraints)
│   │   └── seed_data.sql            # Realistic industrial supply seed data
│   ├── scripts/
│   │   └── init_db.py               # Automated schema & seed execution script
│   ├── utils/
│   │   ├── db_handler.py            # ACID transaction engine & connection pool
│   │   └── forecasting.py           # ML demand forecasting & burn rate model
│   ├── app.py                       # 5-Tab Streamlit enterprise dashboard
│   ├── DEPLOYMENT.md                # Production Cloud DBaaS & Streamlit playbook
│   ├── requirements.txt             # Exact pinned dependencies
│   └── README.md                    # Dedicated inventory system documentation
│
├── cloudpulse-ai/                   # ⚡ Predictive Cloud Workload Forecasting & Auto-Scaling
│   ├── backend/
│   │   ├── app/
│   │   │   ├── ml/                  # Workload generator, preprocessor, RF regressor
│   │   │   ├── simulation/          # Virtual instance, Reactive & Predictive policies, engine
│   │   │   ├── routes/              # FastAPI endpoints (health, dataset, forecast, simulation)
│   │   │   └── database.py          # SQLite engine & ORM models
│   │   ├── data/                    # Reproducible synthetic workload telemetry
│   │   ├── tests/                   # Full Pytest test suite (ML, simulation, APIs)
│   │   └── requirements.txt         # Pinned backend dependencies
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── components/          # Reusable dashboard widgets (MetricCard, InstanceCard, etc.)
│   │   │   ├── pages/               # 7 interactive views (Overview, Analytics, Simulation Lab)
│   │   │   └── api/                 # Strongly typed Axios HTTP client
│   │   └── package.json             # React 18 + Vite + Tailwind dependencies
│   └── README.md                    # Comprehensive academic & technical report
│
├── Cloud-Cost-Optimization/         # 💰 Multi-Cloud Cost Optimization & Resource Governor
│   ├── app.py                       # Dual-mode Python dashboard (Streamlit UI & CLI auditor)
│   ├── governor.py                  # Core Resource Governor analytics engine
│   ├── requirements.txt             # Python analytics & dashboard dependencies
│   ├── backend/                     # Full-stack Go Gin REST API server
│   ├── frontend/                    # Next.js 15 TypeScript cost monitoring portal
│   ├── docker-compose.yml           # TimescaleDB & Redis container configuration
│   └── README.md                    # Dedicated project overview & quickstart
│
├── Internet-Speed-Monitoring/       # 📶 Real-Time Internet Speed & Network Reliability Monitor
│   ├── monitor.py                   # Automated network telemetry daemon & benchmark engine
│   ├── app.py                       # Interactive Streamlit dashboard & CLI reporter
│   ├── requirements.txt             # Python analytics & visualization dependencies
│   ├── telemetry.db                 # SQLite database for historical time-series metrics
│   ├── telemetry.csv                # Exportable CSV telemetry logs
│   ├── index.html                   # Lightweight HTML5 speedtest web interface
│   ├── speedtest.js                 # Client-side speed test orchestration engine
│   ├── speedtest_worker.js          # Web Worker handling async XHR download/upload
│   ├── backend/                     # Multi-language backend telemetry endpoints (PHP, Node, Go)
│   ├── docker/                      # Container configurations & Dockerfiles
│   └── README.md                    # Dedicated project documentation & quickstart playbook
│
├── Website-Uptime-Monitoring/        # 🌐 Cloud Website Uptime & Reliability Monitor
│   ├── app.py                       # Dual-mode Python dashboard (Streamlit UI & CLI auditor)
│   ├── checker.py                   # Core polling engine, SSL tracker & incident manager
│   ├── endpoints.json               # Configurable endpoint target registry
│   ├── requirements.txt             # Python analytics & dashboard dependencies
│   ├── uptime_monitor.db            # SQLite persistence store for health checks & incidents
│   ├── logs/                        # Historical alert dispatches and probe logs
│   ├── server/                      # Full-stack Node.js backend services
│   ├── src/                         # Vue 3 / Vite frontend application
│   └── README.md                    # Dedicated project overview & quickstart
│
├── Cloud-Password-Manager/          # 🔐 Zero-Knowledge Cloud Password Manager & Vault
│   ├── app.py                       # Interactive Streamlit vault dashboard & web application
│   ├── main.py                      # Dual-mode interactive CLI console & crypto benchmark auditor
│   ├── crypto.py                    # Cryptographic engine (AES-256-GCM, Argon2id, PBKDF2, Entropy)
│   ├── db.py                        # SQLite persistence layer, authentication verifier & audit logger
│   ├── schema.sql                   # Database schema definitions with zero-knowledge constraints
│   ├── test_crypto.py               # Automated pytest suite (key derivation, AES-GCM, tamper checks)
│   ├── requirements.txt             # Pinned Python package dependencies
│   ├── VAULTWARDEN_GUIDE.md         # Preserved upstream enterprise Rust vault documentation
│   └── README.md                    # Dedicated zero-knowledge project overview & documentation
│
├── Cloud-Utility-Tools-Website/       # 🛠️ Cloud Utility Tools Suite & Web Platform
│   ├── app.py                       # Dual-mode Python dashboard (Streamlit UI & CLI launcher)
│   ├── main.py                      # FastAPI REST service & CLI diagnostic audit
│   ├── test_tools.py                # Automated Pytest validation test suite
│   ├── requirements.txt             # Pinned backend Python dependencies
│   ├── tools/                       # Modular micro-tools (DNS, CIDR, JWT, Hashes, SSL)
│   ├── static/                      # Custom dark-mode styles and vector branding
│   ├── templates/                   # Exportable audit templates and schemas
│   ├── components/                  # Reusable dashboard metric cards and status badges
│   ├── src/                         # Upstream Vue 3 / Vite web application
│   └── README.md                    # Exhaustive project documentation & API guide
│
├── requirements.txt                 # Root Streamlit Cloud dependencies
└── README.md                        # Master repository documentation
```

---

## ⚡ Quick Start: Internet Speed & Network Reliability Monitor

```bash
# 1. Clone repository
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/Internet-Speed-Monitoring

# 2. Virtual environment setup
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run benchmark or start telemetry daemon
python monitor.py               # One-off benchmark
python monitor.py --daemon      # Periodic background monitor

# 5. Launch Interactive Dashboard
streamlit run app.py
```

---

## ⚡ Quick Start: Cloud Cost Optimization

```bash
# 1. Clone repository
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/Cloud-Cost-Optimization

# 2. Virtual environment setup
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch Interactive Dashboard (Terminal 1)
streamlit run app.py

# Or run terminal audit report:
python app.py
```

---

## ⚡ Quick Start: CloudPulse AI

```bash
# 1. Clone repository
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/cloudpulse-ai

# 2. Launch FastAPI Backend (Terminal 1)
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 3. Launch React Frontend (Terminal 2)
cd ../frontend
npm install
npm run dev
```

---

## ⚡ Quick Start: Cloud AQI Predictor

```bash
# 1. Clone repository
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/cloud-aqi-predictor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch FastAPI backend (Terminal 1)
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload

# 4. Launch Streamlit UI (Terminal 2)
streamlit run frontend/dashboard.py
```

---

## ⚡ Quick Start: Website Uptime Monitoring

```bash
# 1. Clone repository
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/Website-Uptime-Monitoring

# 2. Virtual environment setup
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run polling/checker engine (Terminal 1)
python checker.py --once
# Or run continuous daemon:
# python checker.py --interval 30

# 5. Launch Interactive Dashboard (Terminal 2)
streamlit run app.py

# Or run terminal audit report:
python app.py
```

---

## ⚡ Quick Start: Cloud Password Manager

```bash
# 1. Clone repository
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/Cloud-Password-Manager

# 2. Virtual environment setup
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run interactive CLI / Crypto Benchmark (Terminal 1)
python main.py
# Or run automated cryptographic benchmark:
# python main.py --demo

# 5. Launch Zero-Knowledge Vault Web Dashboard (Terminal 2)
streamlit run app.py
```

---

## ⚡ Quick Start: Cloud Utility Tools Suite

```bash
# 1. Clone repository
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/Cloud-Utility-Tools-Website

# 2. Virtual environment setup
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch Interactive Web Dashboard (Terminal 1)
streamlit run app.py

# 5. Launch FastAPI REST Service (Terminal 2)
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Or run terminal diagnostic audit:
python main.py --audit
```

---

## 👤 Author

**Rithikesh S**  
- GitHub: [@rithikesh18-rk](https://github.com/rithikesh18-rk)
