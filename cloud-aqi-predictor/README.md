# 🌫️ Cloud-Based Air Quality Index (AQI) Predictor & Forecast

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1.0-EB6424.svg?style=flat&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD Pipeline](https://img.shields.io/badge/GitHub_Actions-Passing-2088FF.svg?style=flat&logo=githubactions&logoColor=white)](https://github.com/rithikesh18-rk/cloud-computing/actions)
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit_Cloud-Live_Demo-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://share.streamlit.io/)

A production-grade, cloud-native Machine Learning atmospheric forecasting application designed to predict real-time **Air Quality Index (AQI)** and provide actionable **EPA-standard health advisories** using multi-pollutant environmental telemetry and meteorological conditions.

---

## 🚀 Live Demo & Web Access

Experience the interactive prediction dashboard online:

| Platform | URL / Access | Status |
| :--- | :--- | :--- |
| **Streamlit Community Cloud** | 🌐 **[Launch Live AQI Predictor App](https://share.streamlit.io/)** | 🟢 Operational |
| **FastAPI Swagger UI Docs** | `http://localhost:8000/docs` | 🟢 Local / Docker |
| **FastAPI Health Check** | `http://localhost:8000/health` | 🟢 Local / Docker |

> **Quick Note:** The Streamlit dashboard operates in **dual-mode** — it leverages direct, cached in-process XGBoost model inference when deployed serverlessly on Streamlit Cloud, and automatically interfaces with the FastAPI REST API when running in connected distributed cloud environments.

---

## 📌 Key Features

- 🔬 **Multi-Pollutant Tracking**: Evaluates real-time concentrations of **PM2.5** ($\mu\text{g/m}^3$), **PM10** ($\mu\text{g/m}^3$), **NO2** ($\text{ppb}$), **SO2** ($\text{ppb}$), and **CO** ($\text{ppm}$).
- 🌡️ **Meteorological Context**: Incorporates ambient temperature ($^\circ\text{C}$) and relative humidity ($\%$) to account for atmospheric dispersion and photochemical smog dynamics.
- ⚡ **High-Accuracy ML Inference**: Powered by a tuned **XGBoost Regressor** trained on 1,500 realistic samples formulated around EPA standard sub-index breakpoints ($R^2 = 0.9991$).
- 🩺 **Dynamic EPA Health Advisories**: Categorizes air quality into 6 official EPA bands (*Good*, *Moderate*, *Unhealthy for Sensitive Groups*, *Unhealthy*, *Very Unhealthy*, *Hazardous*) with actionable public health guidelines.
- 📊 **Interactive Plotly Visualizations**: Features dynamic AQI gauge dials and comparative bar charts contrasting current input readings against EPA baseline safe thresholds.
- 🐳 **Cloud-Native & Containerized**: Fully containerized with Docker multi-stage configuration and automated GitHub Actions CI/CD workflows for testing and validation.

---

## 🏗️ System Architecture

```text
+-------------------------------------------------------------------------+
|                    🌐 Streamlit Web Dashboard UI                        |
|  - Sliders for PM2.5, PM10, NO2, SO2, CO, Temperature, Humidity         |
|  - EPA Category Badges, Health Advisory Cards, Plotly Comparison Charts |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                     ⚡ Inference Router Layer                          |
|  - Queries FastAPI REST API (HTTP POST /predict) if available           |
|  - Seamlessly falls back to in-process cached XGBoost model artifact    |
+------------------+---------------------------------+--------------------+
                   |                                 |
                   v                                 v
+------------------+---------------+  +--------------+--------------------+
|      🚀 FastAPI Cloud Backend     |  |   📦 In-Process Direct Engine     |
|  - Pydantic Request Validation   |  |   - joblib.load('aqi_model.joblib')|
|  - POST /predict, GET /health    |  |   - Cached Model Inference         |
+------------------+---------------+  +--------------+--------------------+
                   |                                 |
                   +----------------+----------------+
                                    |
                                    v
+-----------------------------------+-------------------------------------+
|                   🤖 XGBoost ML Regressor Model                         |
|         (n_estimators=150, learning_rate=0.05, max_depth=5)             |
+-----------------------------------+-------------------------------------+
                                    |
                                    v
+-----------------------------------+-------------------------------------+
|              📋 EPA Standards Categorization & Advisories               |
|  Good (0-50) | Moderate (51-100) | USG (101-150) | Unhealthy (151-200) |
|           Very Unhealthy (201-300) | Hazardous (301-500)                |
+-------------------------------------------------------------------------+
```

---

## 🛠️ Tech Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Machine Learning** | `XGBoost`, `Scikit-Learn`, `Pandas`, `NumPy`, `Joblib` | Gradient boosted decision trees for AQI regression |
| **Backend API** | `FastAPI`, `Uvicorn`, `Pydantic v2` | High-throughput REST API with strict validation |
| **Frontend UI** | `Streamlit`, `Plotly`, `HTML5 / CSS3` | Reactive, glassmorphic analytics dashboard |
| **Testing & Quality** | `Pytest`, `HTTPX`, `Flake8` | Automated unit tests and code linting |
| **Container & CI/CD** | `Docker`, `GitHub Actions` | Automated build, test, and containerization |

---

## 📊 Model Evaluation Performance

```text
==========================================
         MODEL EVALUATION METRICS         
==========================================
 Root Mean Squared Error (RMSE) : 4.1292
 Mean Absolute Error (MAE)      : 2.6504
 R-squared Score (R2)           : 0.9991
==========================================
```

---

## 💻 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/cloud-aqi-predictor
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Train the ML Model (Optional - Pre-trained artifact included)
```bash
python src/train.py
```

### 5. Launch the FastAPI Backend Server
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

### 6. Launch the Streamlit Frontend Dashboard
```bash
streamlit run frontend/dashboard.py
```
- **Dashboard UI**: [http://localhost:8501](http://localhost:8501)

### 7. Run the Automated Test Suite
```bash
pytest tests/ -v
```

---

## 🐳 Docker Deployment

### 1. Build the Docker Image
```bash
docker build -t cloud-aqi-predictor:latest .
```

### 2. Run the Container
```bash
docker run -d \
  -p 8000:8000 \
  -p 8501:8501 \
  --name aqi-service \
  cloud-aqi-predictor:latest
```

### 3. Verify Container Health
```bash
curl -f http://localhost:8000/health
```

---

## 📡 REST API Reference

### `POST /predict`
Performs ML inference on input pollutant and weather parameters.

#### Request Headers
```http
Content-Type: application/json
```

#### Request Payload
```json
{
  "pm25": 45.2,
  "pm10": 80.1,
  "no2": 22.0,
  "so2": 10.5,
  "co": 1.2,
  "temperature": 30.0,
  "humidity": 60.0
}
```

#### Response (`HTTP 200 OK`)
```json
{
  "predicted_aqi": 124.93,
  "category": "Unhealthy for Sensitive Groups",
  "advisory": "Sensitive individuals should reduce exertion",
  "timestamp": "2026-08-27T14:35:03.232411+00:00"
}
```

---

## 📂 Project Directory Structure

```text
cloud-aqi-predictor/
├── data/
│   └── aqi_dataset.csv          # 1500-sample environmental training dataset
├── frontend/
│   └── dashboard.py             # Streamlit visualization & inference dashboard
├── models/
│   └── aqi_model.joblib         # Serialized XGBoost Regressor model artifact
├── src/
│   ├── app.py                   # FastAPI REST application
│   ├── schemas.py               # Pydantic request & response schemas
│   ├── train.py                 # Dataset generator, training pipeline & evaluator
│   └── utils.py                 # EPA standard categorization & health advisory logic
├── tests/
│   └── test_api.py              # Automated test suite for endpoints
├── .dockerignore                # Build context exclusion rules
├── .gitignore                   # Version control ignore rules
├── Dockerfile                   # Production multi-stage Docker container definition
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 👤 Author

**Rithikesh S**  
- GitHub: [@rithikesh18-rk](https://github.com/rithikesh18-rk)
