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
| **Cloud-Based AQI Predictor** | 🎈 Streamlit Cloud | [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cloudaqipredictor-mxappeflcb2uurjcacex2uq.streamlit.app)<br>👉 [https://cloudaqipredictor-mxappeflcb2uurjcacex2uq.streamlit.app](https://cloudaqipredictor-mxappeflcb2uurjcacex2uq.streamlit.app) | 🟢 Active |
| **Employee Management System** | ⚡ Render Cloud | 🚀 **[Launch Live HR Portal](https://employee-management-system-bv3y.onrender.com/)** | 🟢 Active |
| **Attendance Management System** | 💻 Local / VM | `http://127.0.0.1:5000` | 🟢 Verified |

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

- **Description:** A full-stack, responsive academic attendance management platform built for educational institutions. Features multi-role authentication (Admin, Faculty, Student), dynamic institutional branding, class attendance marking with bulk toggles, attendance percentage calculations with shortage (< 75%) alerts, Chart.js analytics, and downloadable PDF & Excel export capabilities.
- **Technologies Used:** Python, Flask, Flask-SQLAlchemy, PyMySQL / SQLite, Bootstrap 5, Chart.js, ReportLab (PDF), OpenPyXL (Excel).
- **Subdirectory:** [`Attendance-Management-System/`](./Attendance-Management-System/)

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
├── requirements.txt                 # Root Streamlit Cloud dependencies
└── README.md                        # Master repository documentation
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
