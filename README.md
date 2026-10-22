# Cloud Computing Projects

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

| Project | Platform | Access Link / Button | Status |
| :--- | :--- | :--- | :--- |
| **Cloud-Based AQI Predictor** | 🎈 Streamlit Cloud | [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cloudaqipredictor-mxappeflcb2uurjcacex2uq.streamlit.app)<br>🚀 [Launch Live AQI Predictor](https://cloudaqipredictor-mxappeflcb2uurjcacex2uq.streamlit.app/) | 🟢 Active |
| **Employee Management System** | ⚡ Render Cloud | 🚀 **[Launch Live HR Portal](https://employee-management-system-bv3y.onrender.com/)** | 🟢 Active |
| **Attendance Management System** | ⚡ Render Cloud | 🚀 [Launch Live Attendance System](https://attendance-management-system-1-3fey.onrender.com/) | 🟢 Active |
| **Multi-Warehouse Inventory System** | 🎈 Streamlit Cloud | 🚀 [Launch Cloud Inventory Orchestrator](https://rk-inventory-cloud.streamlit.app/) | 🟢 Active |
| **CloudPulse AI** | ⚡ FastAPI + React Cloud Dashboard | 🚀 [Explore CloudPulse AI](./cloudpulse-ai/) | 🟢 Active |

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
├── requirements.txt                 # Root Streamlit Cloud dependencies
└── README.md                        # Master repository documentation
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

## 👤 Author

**Rithikesh S**  
- GitHub: [@rithikesh18-rk](https://github.com/rithikesh18-rk)
