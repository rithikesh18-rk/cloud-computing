"""
Cloud-Based AQI Predictor & Forecast Dashboard
Built with Streamlit and integrated with direct ML model inference & FastAPI backend
"""

import sys
from pathlib import Path

# Add project root and subdirectories to sys.path so modules in src/ resolve reliably
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import streamlit as st
import requests
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone

# API Configuration
API_BASE_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"

# Page Configuration
st.set_page_config(
    page_title="🌫️ Cloud AQI Predictor & Forecast",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    
    .aqi-card {
        padding: 24px;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .badge-status {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .action-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 16px;
        backdrop-filter: blur(8px);
    }
    
    .metric-subtext {
        font-size: 0.88rem;
        opacity: 0.85;
    }
</style>
""", unsafe_allow_html=True)


# Self-contained EPA Utility Functions
def get_aqi_category(aqi: float) -> tuple[str, str]:
    """Determine the EPA AQI category and associated health advisory."""
    if aqi <= 50:
        return "Good", "Air quality is satisfactory"
    elif aqi <= 100:
        return "Moderate", "Acceptable air quality"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "Sensitive individuals should reduce exertion"
    elif aqi <= 200:
        return "Unhealthy", "Everyone may begin to experience health effects"
    elif aqi <= 300:
        return "Very Unhealthy", "Health alert: serious risk"
    else:
        return "Hazardous", "Emergency conditions: entire population affected"


def calculate_sub_index(conc: float, breakpoints: list) -> float:
    """Calculate the sub-index for a single pollutant based on EPA piecewise linear formula."""
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if bp_lo <= conc <= bp_hi:
            return ((i_hi - i_lo) / (bp_hi - bp_lo)) * (conc - bp_lo) + i_lo
    bp_lo, bp_hi, i_lo, i_hi = breakpoints[-1]
    if conc > bp_hi:
        return ((i_hi - i_lo) / (bp_hi - bp_lo)) * (conc - bp_lo) + i_lo
    return 0.0


def calculate_epa_aqi(pm25: float, pm10: float, no2: float, so2: float, co: float) -> float:
    """Calculate the EPA AQI as the maximum of individual pollutant sub-indices."""
    pm25_bp = [(0.0, 12.0, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150), (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300), (250.5, 500.0, 301, 500)]
    pm10_bp = [(0.0, 54.0, 0, 50), (55.0, 154.0, 51, 100), (155.0, 254.0, 101, 150), (255.0, 354.0, 151, 200), (355.0, 424.0, 201, 300), (425.0, 600.0, 301, 500)]
    no2_bp = [(0.0, 53.0, 0, 50), (54.0, 100.0, 51, 100), (101.0, 360.0, 101, 150), (361.0, 649.0, 151, 200), (650.0, 1249.0, 201, 300), (1250.0, 2049.0, 301, 500)]
    so2_bp = [(0.0, 35.0, 0, 50), (36.0, 75.0, 51, 100), (76.0, 185.0, 101, 150), (186.0, 304.0, 151, 200), (305.0, 604.0, 201, 300), (605.0, 1004.0, 301, 500)]
    co_bp = [(0.0, 4.4, 0, 50), (4.5, 9.4, 51, 100), (9.5, 12.4, 101, 150), (12.5, 15.4, 151, 200), (15.5, 30.4, 201, 300), (30.5, 50.0, 301, 500)]

    i_pm25 = calculate_sub_index(pm25, pm25_bp)
    i_pm10 = calculate_sub_index(pm10, pm10_bp)
    i_no2 = calculate_sub_index(no2, no2_bp)
    i_so2 = calculate_sub_index(so2, so2_bp)
    i_co = calculate_sub_index(co, co_bp)

    return max(i_pm25, i_pm10, i_no2, i_so2, i_co)


@st.cache_resource
def load_local_model():
    """Locate and load the trained XGBoost model artifact for standalone inference."""
    candidates = [
        PROJECT_ROOT / "models" / "aqi_model.joblib",
        CURRENT_DIR.parent / "models" / "aqi_model.joblib",
        Path.cwd() / "cloud-aqi-predictor" / "models" / "aqi_model.joblib",
        Path.cwd() / "models" / "aqi_model.joblib",
    ]
    for model_file in candidates:
        if model_file.exists():
            try:
                loaded_model = joblib.load(model_file)
                return loaded_model, model_file
            except Exception:
                continue
    return None, None


def check_system_status() -> tuple[str, str]:
    """Check API and direct ML model readiness."""
    # Check FastAPI
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=0.8)
        if response.status_code == 200 and response.json().get("model_loaded", False):
            return "#10B981", "🟢 Live API Connected (FastAPI)"
    except Exception:
        pass

    # Check Local Model
    model, path = load_local_model()
    if model is not None:
        return "#10B981", "🟢 Standalone ML Engine (XGBoost Active)"

    return "#38BDF8", "🔵 EPA Standards Forecast Engine"


def get_prediction(payload: dict) -> dict:
    """Obtain prediction via API or standalone direct model inference."""
    # 1. Try FastAPI Backend
    try:
        res = requests.post(PREDICT_ENDPOINT, json=payload, timeout=1.0)
        if res.status_code == 200:
            data = res.json()
            data["source"] = "FastAPI Cloud Backend"
            return data
    except Exception:
        pass

    # 2. Try Direct Local Model Inference
    model, _ = load_local_model()
    if model is not None:
        try:
            df = pd.DataFrame([{
                "PM2.5": payload["pm25"],
                "PM10": payload["pm10"],
                "NO2": payload["no2"],
                "SO2": payload["so2"],
                "CO": payload["co"],
                "Temperature": payload["temperature"],
                "Humidity": payload["humidity"]
            }])
            raw_pred = model.predict(df)[0]
            predicted_aqi = round(float(np.clip(raw_pred, 0.0, 500.0)), 2)
            category, advisory = get_aqi_category(predicted_aqi)
            return {
                "predicted_aqi": predicted_aqi,
                "category": category,
                "advisory": advisory,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "Local XGBoost ML Engine"
            }
        except Exception:
            pass

    # 3. EPA Standards Calculation Fallback
    raw_aqi = calculate_epa_aqi(payload["pm25"], payload["pm10"], payload["no2"], payload["so2"], payload["co"])
    temp_mod = (payload["temperature"] - 25.0) * 0.15
    humidity_mod = (payload["humidity"] - 50.0) * 0.1
    final_aqi = round(float(np.clip(raw_aqi + temp_mod + humidity_mod, 0.0, 500.0)), 2)
    category, advisory = get_aqi_category(final_aqi)
    return {
        "predicted_aqi": final_aqi,
        "category": category,
        "advisory": advisory,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "EPA Standard Engine"
    }


def get_category_color(category: str) -> dict:
    """Return styling colors for each AQI category."""
    category_map = {
        "Good": {
            "bg": "linear-gradient(135deg, #059669 0%, #10B981 100%)",
            "badge": "#10B981",
            "hex": "#10B981",
            "icon": "🟢",
            "level": "Clean & Healthy"
        },
        "Moderate": {
            "bg": "linear-gradient(135deg, #D97706 0%, #F59E0B 100%)",
            "badge": "#F59E0B",
            "hex": "#F59E0B",
            "icon": "🟡",
            "level": "Acceptable"
        },
        "Unhealthy for Sensitive Groups": {
            "bg": "linear-gradient(135deg, #EA580C 0%, #F97316 100%)",
            "badge": "#F97316",
            "hex": "#F97316",
            "icon": "🟠",
            "level": "Caution for Sensitive Groups"
        },
        "Unhealthy": {
            "bg": "linear-gradient(135deg, #DC2626 0%, #EF4444 100%)",
            "badge": "#EF4444",
            "hex": "#EF4444",
            "icon": "🔴",
            "level": "Unhealthy for Everyone"
        },
        "Very Unhealthy": {
            "bg": "linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%)",
            "badge": "#8B5CF6",
            "hex": "#8B5CF6",
            "icon": "🟣",
            "level": "Health Alert: Serious"
        },
        "Hazardous": {
            "bg": "linear-gradient(135deg, #881337 0%, #9F1239 100%)",
            "badge": "#881337",
            "hex": "#881337",
            "icon": "🟤",
            "level": "Emergency Conditions"
        }
    }
    return category_map.get(category, category_map["Moderate"])


# Check System Health
badge_color, health_msg = check_system_status()

# Header Section
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
        <div>
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700; color: #f8fafc;">
                🌫️ Cloud-Based Air Quality (AQI) Predictor
            </h1>
            <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 1.05rem;">
                Machine Learning-powered atmospheric pollution forecasting & EPA health advisory system
            </p>
        </div>
        <div>
            <span class="badge-status" style="background-color: rgba(15, 23, 42, 0.8); color: {badge_color}; border: 1px solid {badge_color};">
                {health_msg}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar - Parameter Controls
st.sidebar.header("🎛️ Atmospheric & Pollutant Controls")
st.sidebar.caption("Adjust pollutant concentrations and meteorological parameters:")

# Quick Presets
with st.sidebar.expander("⚡ Quick Scenario Presets", expanded=False):
    preset = st.radio(
        "Choose Preset:",
        ["Custom", "🌿 Clean Mountain Air", "🚗 Urban Moderate", "🏭 Industrial Heavy", "🔥 Wildfire Smog"]
    )

# Preset Values
defaults = {
    "pm25": 45.0, "pm10": 85.0, "no2": 25.0, "so2": 12.0, "co": 1.5, "temp": 30.0, "humidity": 60.0
}

if preset == "🌿 Clean Mountain Air":
    defaults = {"pm25": 6.0, "pm10": 15.0, "no2": 8.0, "so2": 4.0, "co": 0.4, "temp": 20.0, "humidity": 45.0}
elif preset == "🚗 Urban Moderate":
    defaults = {"pm25": 38.0, "pm10": 75.0, "no2": 35.0, "so2": 18.0, "co": 1.8, "temp": 28.0, "humidity": 55.0}
elif preset == "🏭 Industrial Heavy":
    defaults = {"pm25": 160.0, "pm10": 260.0, "no2": 85.0, "so2": 65.0, "co": 5.5, "temp": 34.0, "humidity": 70.0}
elif preset == "🔥 Wildfire Smog":
    defaults = {"pm25": 350.0, "pm10": 480.0, "no2": 120.0, "so2": 40.0, "co": 8.2, "temp": 38.0, "humidity": 30.0}

pm25 = st.sidebar.slider("PM2.5 (Fine Particulate, µg/m³)", 0.0, 500.0, float(defaults["pm25"]), 0.5, help="Particles ≤ 2.5 micrometers. Major contributor to haze and deep respiratory penetration.")
pm10 = st.sidebar.slider("PM10 (Coarse Particulate, µg/m³)", 0.0, 600.0, float(defaults["pm10"]), 1.0, help="Inhalable particles ≤ 10 micrometers like dust, pollen, and mold.")
no2 = st.sidebar.slider("NO2 (Nitrogen Dioxide, ppb)", 0.0, 200.0, float(defaults["no2"]), 0.5, help="Gaseous pollutant mainly from vehicle emissions and power plants.")
so2 = st.sidebar.slider("SO2 (Sulfur Dioxide, ppb)", 0.0, 100.0, float(defaults["so2"]), 0.5, help="Produced from burning fossil fuels like coal and oil.")
co = st.sidebar.slider("CO (Carbon Monoxide, ppm)", 0.0, 10.0, float(defaults["co"]), 0.1, help="Colorless, odorless gas emitted by combustion engines.")

st.sidebar.markdown("---")
st.sidebar.subheader("🌡️ Weather Conditions")
temperature = st.sidebar.slider("Temperature (°C)", 10.0, 50.0, float(defaults["temp"]), 0.5)
humidity = st.sidebar.slider("Relative Humidity (%)", 10.0, 100.0, float(defaults["humidity"]), 1.0)

predict_btn = st.sidebar.button("🔮 Predict AQI", type="primary", use_container_width=True)

# Prepare Payload
payload = {
    "pm25": pm25,
    "pm10": pm10,
    "no2": no2,
    "so2": so2,
    "co": co,
    "temperature": temperature,
    "humidity": humidity
}

# Main Prediction Flow
if predict_btn or "last_prediction" not in st.session_state:
    st.session_state["last_prediction"] = get_prediction(payload)

prediction_data = st.session_state.get("last_prediction")

# Render Prediction Results
if prediction_data:
    aqi_val = prediction_data["predicted_aqi"]
    category = prediction_data["category"]
    advisory = prediction_data["advisory"]
    source = prediction_data.get("source", "ML Engine")
    color_info = get_category_color(category)

    # Top Row Cards
    col_aqi, col_cat, col_env = st.columns([1.2, 1.3, 1.5])

    with col_aqi:
        st.markdown(f"""
        <div class="aqi-card" style="background: {color_info['bg']};">
            <div style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">Predicted AQI Score</div>
            <div style="font-size: 4rem; font-weight: 800; line-height: 1.1; margin: 10px 0;">{aqi_val:.1f}</div>
            <div class="metric-subtext">{color_info['icon']} Scale Range: 0 — 500</div>
        </div>
        """, unsafe_allow_html=True)

    with col_cat:
        st.markdown(f"""
        <div class="aqi-card" style="background: #1e293b; border-left: 6px solid {color_info['hex']};">
            <div style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8;">EPA Classification</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {color_info['hex']}; margin: 14px 0 6px 0;">{category}</div>
            <div class="metric-subtext" style="color: #cbd5e1;">Status: <strong>{color_info['level']}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with col_env:
        st.markdown(f"""
        <div class="aqi-card" style="background: #1e293b; border-left: 6px solid #38bdf8;">
            <div style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8;">Meteorological Context</div>
            <div style="display: flex; justify-content: space-around; margin-top: 15px;">
                <div>
                    <div style="font-size: 1.7rem; font-weight: 700; color: #f8fafc;">🌡️ {temperature}°C</div>
                    <div class="metric-subtext" style="color: #94a3b8;">Ambient Temp</div>
                </div>
                <div>
                    <div style="font-size: 1.7rem; font-weight: 700; color: #f8fafc;">💧 {humidity}%</div>
                    <div class="metric-subtext" style="color: #94a3b8;">Rel. Humidity</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Middle Section - Health Advisory & Action Plans
    st.markdown("### 📋 Health Advisory & Safety Guidelines")
    
    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.markdown(f"""
        <div class="action-card" style="border-left: 4px solid {color_info['hex']};">
            <h4 style="margin-top: 0; color: #f8fafc;">🩺 Official EPA Advisory</h4>
            <p style="font-size: 1.05rem; color: #e2e8f0; margin-bottom: 0;">
                "{advisory}"
            </p>
        </div>
        """, unsafe_allow_html=True)

    with rec_col2:
        if aqi_val <= 50:
            action_html = "✅ Great day for outdoor activities, sports, and ventilation.<br>✅ Air quality is ideal for all individuals."
        elif aqi_val <= 100:
            action_html = "⚠️ Unusually sensitive individuals should monitor symptoms.<br>✅ General public can safely enjoy outdoor activities."
        elif aqi_val <= 150:
            action_html = "😷 Sensitive groups (children, elderly, asthmatics) should reduce strenuous outdoor exertion.<br>🪟 Consider closing windows during peak traffic hours."
        elif aqi_val <= 200:
            action_html = "🚫 Everyone should reduce prolonged outdoor exertion.<br>😷 Wear N95/KN95 masks if heading outdoors.<br>🏠 Run indoor HEPA air purifiers."
        elif aqi_val <= 300:
            action_html = "🚨 Avoid outdoor physical activities.<br>🚪 Keep all windows and doors closed.<br>😷 High-efficiency respirator masks mandatory outdoors."
        else:
            action_html = "🛑 Emergency Health Warning: Remain indoors with air filtration active.<br>🚫 Avoid all outdoor physical activity."

        st.markdown(f"""
        <div class="action-card" style="border-left: 4px solid #38bdf8;">
            <h4 style="margin-top: 0; color: #f8fafc;">🛡️ Recommended Action Steps</h4>
            <p style="font-size: 0.95rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 0;">
                {action_html}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Bottom Visuals
    st.markdown("### 📊 Pollutant Concentration Breakdown vs EPA Baseline Thresholds")
    
    chart_col1, chart_col2 = st.columns([2, 1])

    with chart_col1:
        pollutants_df = pd.DataFrame([
            {"Pollutant": "PM2.5", "Concentration": pm25, "Baseline (Good)": 12.0, "Unit": "µg/m³"},
            {"Pollutant": "PM10", "Concentration": pm10, "Baseline (Good)": 54.0, "Unit": "µg/m³"},
            {"Pollutant": "NO2", "Concentration": no2, "Baseline (Good)": 53.0, "Unit": "ppb"},
            {"Pollutant": "SO2", "Concentration": so2, "Baseline (Good)": 35.0, "Unit": "ppb"},
            {"Pollutant": "CO", "Concentration": co, "Baseline (Good)": 4.4, "Unit": "ppm"},
        ])

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pollutants_df["Pollutant"],
            y=pollutants_df["Concentration"],
            name="Current Input Level",
            marker_color="#38bdf8",
            text=[f"{val} {u}" for val, u in zip(pollutants_df["Concentration"], pollutants_df["Unit"])],
            textposition="auto"
        ))
        fig.add_trace(go.Bar(
            x=pollutants_df["Pollutant"],
            y=pollutants_df["Baseline (Good)"],
            name="EPA Safe Baseline (Good)",
            marker_color="#10b981",
            text=[f"{val} {u}" for val, u in zip(pollutants_df["Baseline (Good)"], pollutants_df["Unit"])],
            textposition="auto"
        ))

        fig.update_layout(
            barmode="group",
            title="Current Input vs EPA Safe Thresholds",
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.5)",
            plot_bgcolor="rgba(15, 23, 42, 0.5)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            height=340
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "AQI Gauge", 'font': {'size': 18, 'color': '#f8fafc'}},
            gauge={
                'axis': {'range': [0, 500], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': color_info['hex'], 'thickness': 0.3},
                'bgcolor': "rgba(30, 41, 59, 0.7)",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(16, 185, 129, 0.3)'},
                    {'range': [50, 100], 'color': 'rgba(245, 158, 11, 0.3)'},
                    {'range': [100, 150], 'color': 'rgba(249, 115, 22, 0.3)'},
                    {'range': [150, 200], 'color': 'rgba(239, 68, 68, 0.3)'},
                    {'range': [200, 300], 'color': 'rgba(139, 92, 246, 0.3)'},
                    {'range': [300, 500], 'color': 'rgba(136, 19, 55, 0.4)'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 3},
                    'thickness': 0.8,
                    'value': aqi_val
                }
            }
        ))
        gauge_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.5)",
            plot_bgcolor="rgba(15, 23, 42, 0.5)",
            margin=dict(l=20, r=20, t=40, b=20),
            height=340
        )
        st.plotly_chart(gauge_fig, use_container_width=True)

# Footer
st.markdown("---")
st.caption(f"⚡ Cloud AQI Predictor | Inference Engine: `{prediction_data.get('source', 'XGBoost ML')}` | Model: XGBoost Regressor | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
