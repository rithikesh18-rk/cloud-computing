# Cloud Cost Optimization & Resource Governor

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Go](https://img.shields.io/badge/Go-1.21%2B-00ADD8.svg?style=flat&logo=go&logoColor=white)](https://golang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15.2-000000.svg?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Multi-Cloud](https://img.shields.io/badge/Cloud%20APIs-AWS%20%7C%20GCP%20%7C%20Azure-FF9900.svg?style=flat&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose%20Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An enterprise-grade, automated multi-cloud resource monitoring, rightsizing engine, idle-instance detection suite, and cost-allocation governor.

---

## 📌 Problem Statement

Modern enterprise engineering organizations leverage heterogeneous multi-cloud deployments across Amazon Web Services (AWS), Google Cloud Platform (GCP), and Microsoft Azure. However, decentralized provisioning, lack of automated lifecycle policies, and absent real-time telemetry lead to:

1. **Cloud Over-Provisioning:** Virtual machine instances, memory tiers, and IOPS allocations provisioned at peak capacity that operate at under 15% continuous utilization.
2. **Unmonitored Idle Infrastructure (Zombie Resources):** Orphaned development environments, forgotten GPU sandboxes, and abandoned batch runners that continue to incur full compute-hour operational expenditure (OpEx).
3. **Billing Metric Anomalies & Shock:** Silent billing surges caused by misconfigured backup dumps, runaway container clusters, or cross-region egress that are only detected weeks later during monthly invoice reconciliation.
4. **Opaque Multi-Cloud Attribution:** Difficulty mapping cloud spend to business units, environments, and owners without unified tagging governance.

---

## ⚡ Key Capabilities

- **🔍 Resource Utilization Tracking:**
  - Real-time continuous monitoring of compute utilization (average and peak CPU %), physical memory occupancy, and persistent storage IOPS.
  - Multi-cloud fleet telemetry ingestion across AWS EC2, GCP Compute Engine, and Azure Virtual Machines.
  - Dynamic classification of compute health (Underutilized `< 15%`, Optimal `15–75%`, Overprovisioned `> 75%`).

- **🚨 Billing Metric Anomaly Detection:**
  - Automated statistical analysis of daily and monthly cloud service line items.
  - Rolling baseline Z-score and interquartile deviation tracking ($>3.0\sigma$ alert threshold).
  - Automated root cause attribution (e.g., untagged GPU instances, runaway training loops, uncompressed cross-region storage dumps).

- **🎯 Rightsizing Recommendations & Automated Idle Governor:**
  - Automated detection of zombie infrastructure (average CPU $< 5\%$ and peak $< 10\%$ for $\ge 7$ days).
  - Downsizing recommendation matrix that matches real utilization against multi-cloud instance pricing catalogs (e.g., downscaling `m5.4xlarge` $\rightarrow$ `m5.large`).
  - Automated governance actions: `TAG_AND_SHUTDOWN`, `RIGHTSIZE_DOWNGRADE`, and `MAINTAIN`.

- **📈 Interactive Cost Breakdown & Savings Projection:**
  - Visual spend breakdown across Cloud Providers (AWS, GCP, Azure), Service Categories (Compute, Storage, Database, Network), and Environments (Production, Staging, Dev, QA).
  - 12-month forward cumulative savings simulator modeling phased governance rollout with custom optimization targets.

---

## 🛠️ Technology Stack

| Domain | Technologies |
| :--- | :--- |
| **Core Analytics & Governance** | Python 3.11+, Pandas, NumPy, Scikit-Learn |
| **Visual Analytics Dashboard** | Streamlit 1.38+, Plotly Express & Graph Objects |
| **Full-Stack Microservices** | Go 1.21+ (Gin Web Framework, GORM ORM) |
| **Frontend Web Portal** | Next.js 15 (React 19, TypeScript, Tailwind CSS, Recharts, Lucide Icons) |
| **Storage & Caching** | PostgreSQL 15 + TimescaleDB (Time-series billing records), Redis 7 |
| **Cloud Integrations** | AWS SDK (Cost Explorer / CloudWatch), GCP Cloud Billing API, Azure Cost Management API |
| **Containerization** | Docker, Docker Compose |

---

## 📁 Project Directory Structure

```text
Cloud-Cost-Optimization/
│
├── app.py                     # Dual-mode Python entrypoint: Interactive Streamlit UI & CLI Auditor
├── governor.py                # Core Resource Governor engine: catalog, telemetry, heuristics & anomalies
├── requirements.txt           # Python analytics & dashboard dependencies
│
├── backend/                   # Full-Stack Go Microservice Server
│   ├── cmd/
│   │   ├── api/main.go        # Gin REST API server (listening on port 8080)
│   │   └── migrator/main.go   # TimescaleDB & PostgreSQL schema migrator
│   ├── internal/
│   │   ├── config/            # Environment & database configurations
│   │   ├── handlers/          # HTTP request handlers (auth, accounts, costs, recommendations)
│   │   ├── models/            # Domain entities (User, CloudAccount, CostRecord, Recommendation)
│   │   ├── repository/        # PostgreSQL data access layer
│   │   └── services/          # Multi-cloud collectors (AWS, GCP, Azure) & mock generator
│   ├── go.mod                 # Go module definition
│   └── Dockerfile             # Multi-stage production container
│
├── frontend/                  # Next.js 15 Web Application
│   ├── app/                   # App Router (login, register, dashboard, accounts, recommendations)
│   ├── components/            # Reusable UI widgets (cards, navigation, theme toggle)
│   ├── lib/                   # API clients and Zustand state stores
│   ├── package.json           # Next.js, React, Tailwind CSS dependencies
│   ├── tsconfig.json          # TypeScript compiler configuration
│   └── Dockerfile             # Standalone production Next.js build
│
├── docker-compose.yml         # Container orchestration (TimescaleDB, Redis, API, Frontend)
├── Makefile                   # Development automation targets (up, down, test)
├── railway.json               # Cloud PaaS deployment configuration
├── .env.example               # Environment variables template
├── Complete Startup Guide     # Comprehensive end-to-end deployment documentation
├── Production Architecture.txt# Multi-tier system topology specification
└── README.md                  # Project documentation (this file)
```

---

## 🚀 Quickstart Guide

### Option 1: Python Dashboard & Resource Governor (Instant)

Run the Python analytics dashboard and resource governor directly:

#### 1. Virtual Environment Setup
```bash
# Navigate to the project directory
cd Cloud-Cost-Optimization

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd.exe):
venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Execution Commands
```bash
# Launch the Interactive Visual Analytics Dashboard (Web UI on http://localhost:8501)
streamlit run app.py

# Or run the Automated Terminal Cost Audit CLI:
python app.py
```

---

### Option 2: Full-Stack Go & Next.js Microservices Stack

To run the decoupled full-stack architecture with Go API and Next.js frontend:

#### 1. Configure Environment
```bash
cp .env.example .env
```

#### 2. Launch Supporting Databases via Docker Compose
```bash
docker compose up -d postgres redis
```

#### 3. Launch the Go API Server (Terminal 1)
```bash
cd backend
go run cmd/api/main.go
# API server initializes on http://localhost:8080
```

#### 4. Launch the Next.js Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
# Frontend dashboard accessible at http://localhost:3000
```

---

## 📊 Sample Terminal Audit Output

```text
================================================================================
 [CLOUD COST OPTIMIZATION & RESOURCE GOVERNOR] TERMINAL AUDIT REPORT
================================================================================

[*] EXECUTIVE FINANCIAL SUMMARY:
  - Current Monthly Cloud Spend:  $4,879.00
  - Potential Monthly Savings:   $2,612.20 (53.5% waste)
  - Projected Annualized ROI:     $31,346.40 / year
  - Post-Optimization Spend:      $2,266.80
  - Fleet Inventory:              16 instances (6 IDLE, 3 OVERPROVISIONED)

[*] DETECTED IDLE INSTANCES & SHUTDOWN TARGETS:
--------------------------------------------------------------------------------
ID               NAME                         PROV   TYPE             CPU%   COST/MO   ACTION
--------------------------------------------------------------------------------
i-09f1a2b3c4d    dev-batch-indexer-zombie     AWS    m5.4xlarge       2.1    $560.00   SHUTDOWN
i-05b6c7d8e9f    qa-regression-runner         AWS    c5.2xlarge       1.4    $250.00   SHUTDOWN
i-08a9b0c1d2e    ml-feature-extractor-gpu     AWS    g4dn.xlarge      3.8    $384.00   SHUTDOWN
gcp-vm-554433    gcp-dev-analytics-sandbox    GCP    n2-standard-16   4.2    $580.00   SHUTDOWN
gcp-vm-990011    gcp-idle-scraping-worker     GCP    e2-standard-4    0.8    $100.00   SHUTDOWN
az-vm-112233     az-idle-test-load-injector   Azure  Standard_D4s_v5  0.5    $140.00   SHUTDOWN

[*] RIGHTSIZING DOWNGRADE RECOMMENDATIONS:
--------------------------------------------------------------------------------
ID               NAME                     CURRENT        RECOMMENDED    SAVINGS/MO  
--------------------------------------------------------------------------------
i-03d4e5f6a7b    staging-redis-cache      r5.2xlarge     m5.xlarge      $225.00     
gcp-vm-778899    gcp-backup-mirror-sync   e2-standard-4  e2-micro       $93.20      
az-vm-443322     az-dev-sql-replica       Standard_D16s_v5 Standard_D8s_v5 $280.00     

[*] BILLING SPIKE ANOMALIES DETECTED:
--------------------------------------------------------------------------------
DATE         PROVIDER SERVICE            COST       SCORE   ROOT CAUSE
--------------------------------------------------------------------------------
2026-10-04   AWS      S3                 $120.00    4.2s    Uncompressed cross-region database dump dumped to Standard Tier
2026-10-13   GCP      Compute            $198.00    3.8s    Runaway preemptible cluster failing to terminate after training run
2026-10-19   Azure    VirtualMachines    $192.20    3.3s    Dev team provisioned high-memory GPU node in East US without TTL tag
```

---

## 📜 License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.