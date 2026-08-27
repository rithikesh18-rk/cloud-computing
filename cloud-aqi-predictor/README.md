# 🌫️ Cloud-Based Air Quality Index (AQI) Predictor

A production-grade, cloud-native machine learning solution for predicting Air Quality Index (AQI) and generating real-time EPA-standard health advisories based on atmospheric pollutant and weather metrics.

---

## 🌟 Features

- **Machine Learning Engine**: XGBoost Regressor model trained on realistic environmental datasets following EPA piecewise linear standard breakpoints.
- **RESTful Cloud API**: High-performance FastAPI backend with Pydantic request/response validation, CORS middleware, and automatic Swagger docs (`/docs`).
- **Interactive Web Dashboard**: Streamlit frontend featuring dynamic gauge indicators, scenario presets, EPA health advisories, and pollutant breakdown charts against standard baseline thresholds.
- **Containerization & DevOps**: Multi-stage `Dockerfile` with health probes, `.dockerignore`, and GitHub Actions CI/CD workflows for automated linting, test suites, and Docker container verification.

---

## 🏗️ Project Architecture

```
cloud-aqi-predictor/
├── data/
│   └── aqi_dataset.csv          # 1500-sample environmental dataset
├── models/
│   └── aqi_model.joblib         # Serialized XGBoost Regressor model
├── src/
│   ├── app.py                   # FastAPI REST application
│   ├── schemas.py               # Pydantic validation schemas
│   ├── train.py                 # Model training & synthetic data generation pipeline
│   └── utils.py                 # EPA standard AQI categorization & advisories
├── frontend/
│   └── dashboard.py             # Streamlit visualization & inference dashboard
├── tests/
│   └── test_api.py              # Automated endpoint test suite
├── Dockerfile                   # Production container definition
├── .dockerignore                # Build context exclusion rules
├── .gitignore                   # Version control ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 📊 Model Evaluation Metrics

| Metric | Score |
| :--- | :--- |
| **Root Mean Squared Error (RMSE)** | **4.1292** |
| **Mean Absolute Error (MAE)** | **2.6504** |
| **$R^2$ Score (Coefficient of Determination)** | **0.9991** |

---

## 🚀 Quickstart Guide

### 1. Installation
Clone the repository and install requirements:
```bash
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd cloud-computing/cloud-aqi-predictor
pip install -r requirements.txt
```

### 2. Train the Model
```bash
python src/train.py
```

### 3. Launch FastAPI Backend
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Launch Streamlit Dashboard
```bash
streamlit run frontend/dashboard.py
```
- Interactive UI: [http://localhost:8501](http://localhost:8501)

### 5. Run Automated Tests
```bash
pytest tests/ -v
```

---

## 🐳 Docker Deployment

### Build Container
```bash
docker build -t cloud-aqi-predictor:latest .
```

### Run Container
```bash
docker run -d -p 8000:8000 -p 8501:8501 --name aqi-service cloud-aqi-predictor:latest
```

---

## 📡 API Endpoint Reference

### `POST /predict`
#### Request Payload:
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

#### Response:
```json
{
  "predicted_aqi": 124.93,
  "category": "Unhealthy for Sensitive Groups",
  "advisory": "Sensitive individuals should reduce exertion",
  "timestamp": "2026-08-27T14:35:03.232411+00:00"
}
```
