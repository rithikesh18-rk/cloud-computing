"""
Cloud-Based AQI Predictor & Forecast Dashboard
Built with Streamlit and integrated with FastAPI Backend
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

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


def check_api_health() -> tuple[bool, str]:
    """Check if the FastAPI backend is running and model is loaded."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=2.0)
        if response.status_code == 200:
            data = response.json()
            if data.get("model_loaded", False):
                return True, "API Online & Model Ready"
            return True, "API Online (Model Not Loaded)"
        return False, f"API Error: HTTP {response.status_code}"
    except requests.exceptions.RequestException:
        return False, "API Offline (Start FastAPI server at port 8000)"


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


# Check API Health
is_healthy, health_msg = check_api_health()

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
            <span class="badge-status" style="background-color: {'#065f46' if is_healthy else '#7f1d1d'}; color: {'#34d399' if is_healthy else '#f87171'}; border: 1px solid {'#059669' if is_healthy else '#dc2626'};">
                ● {health_msg}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if not is_healthy:
    st.warning("⚠️ **Backend Not Detected**: FastAPI server is not responding at `http://localhost:8000`. To start it, run: `python -m uvicorn src.app:app --port 8000 --reload` in your terminal.")

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

# Main Execution Flow
prediction_data = None

if predict_btn or "last_prediction" not in st.session_state:
    try:
        response = requests.post(PREDICT_ENDPOINT, json=payload, timeout=3.0)
        if response.status_code == 200:
            prediction_data = response.json()
            st.session_state["last_prediction"] = prediction_data
        else:
            st.error(f"Prediction failed with server status code: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as err:
        st.warning(f"Could not connect to FastAPI server ({err}). Demonstrating with local fallback calculation.")
        # Fallback estimation for standalone UI preview
        from src.train import calculate_epa_aqi
        from src.utils import get_aqi_category
        raw_aqi = calculate_epa_aqi(pm25, pm10, no2, so2, co)
        temp_mod = (temperature - 25.0) * 0.15
        humidity_mod = (humidity - 50.0) * 0.1
        final_aqi = round(float(np.clip(raw_aqi + temp_mod + humidity_mod, 0.0, 500.0)), 2)
        cat, adv = get_aqi_category(final_aqi)
        prediction_data = {
            "predicted_aqi": final_aqi,
            "category": cat,
            "advisory": adv,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        st.session_state["last_prediction"] = prediction_data
else:
    prediction_data = st.session_state.get("last_prediction")

# Render Prediction Results
if prediction_data:
    aqi_val = prediction_data["predicted_aqi"]
    category = prediction_data["category"]
    advisory = prediction_data["advisory"]
    timestamp = prediction_data.get("timestamp", "N/A")
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
        # Dynamic recommended action bullets based on severity
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
        # Benchmark comparisons
        pollutants_df = pd.DataFrame([
            {"Pollutant": "PM2.5", "Concentration": pm25, "Baseline (Good)": 12.0, "Unit": "µg/m³", "Ratio": pm25 / 12.0},
            {"Pollutant": "PM10", "Concentration": pm10, "Baseline (Good)": 54.0, "Unit": "µg/m³", "Ratio": pm10 / 54.0},
            {"Pollutant": "NO2", "Concentration": no2, "Baseline (Good)": 53.0, "Unit": "ppb", "Ratio": no2 / 53.0},
            {"Pollutant": "SO2", "Concentration": so2, "Baseline (Good)": 35.0, "Unit": "ppb", "Ratio": so2 / 35.0},
            {"Pollutant": "CO", "Concentration": co, "Baseline (Good)": 4.4, "Unit": "ppm", "Ratio": co / 4.4},
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
        # Gauge Chart for AQI
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
st.caption(f"⚡ Cloud-Based AQI Predictor | Model: XGBoost Regressor | API Endpoint: `{API_BASE_URL}` | Last inference: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
