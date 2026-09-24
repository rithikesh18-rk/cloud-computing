"""
Demand Analytics and Stockout Prediction Module
utils/forecasting.py

Engineered for:
- Daily consumption time-series aggregation from transaction logs
- Exponential Smoothing & Linear Trend Estimation
- Estimated Days Until Stockout (EDUS) modeling
- Dynamic replenishment recommendation based on lead time and safety stock
- Interactive Plotly consumption trends and 14-day depletion curves
"""

import math
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional, Tuple, List

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. Historical Consumption Aggregation
# -----------------------------------------------------------------------------

def aggregate_daily_consumption(
    transactions_df: pd.DataFrame,
    product_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    days_back: int = 30
) -> pd.DataFrame:
    """
    Extracts and aggregates daily consumption (outbound dispatches and transfers)
    over a continuous date range. Ensures zero-consumption days are accounted for.
    """
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=days_back - 1)
    date_index = [start_date + timedelta(days=i) for i in range(days_back)]
    
    # Initialize base continuous time-series
    ts_df = pd.DataFrame({"date": date_index, "consumption": 0.0, "transaction_count": 0})
    ts_df.set_index("date", inplace=True)

    if transactions_df is None or transactions_df.empty:
        return ts_df.reset_index()

    df = transactions_df.copy()

    # Filter by product and warehouse if specified
    if product_id is not None and "product_id" in df.columns:
        df = df[df["product_id"] == product_id]
    elif product_id is not None and "sku" in df.columns:
        # Fallback if product_id is checked via SKU
        pass

    if warehouse_id is not None and "warehouse_id" in df.columns:
        df = df[df["warehouse_id"] == warehouse_id]

    # Outbound consumption is defined by DISPATCH transactions or negative change_quantity
    if "transaction_type" in df.columns:
        consumption_mask = (df["transaction_type"] == "DISPATCH") | (df["change_quantity"] < 0)
    else:
        consumption_mask = df["change_quantity"] < 0

    df_out = df[consumption_mask].copy()

    if df_out.empty:
        return ts_df.reset_index()

    # Parse and normalize dates
    df_out["txn_date"] = pd.to_datetime(df_out["created_at"]).dt.date
    df_out["units_out"] = df_out["change_quantity"].abs()

    # Aggregate by date
    daily_agg = df_out.groupby("txn_date").agg(
        consumption=("units_out", "sum"),
        transaction_count=("units_out", "count")
    )

    # Merge with continuous calendar index
    merged = ts_df.join(daily_agg, rsuffix="_actual")
    merged["consumption"] = merged["consumption_actual"].fillna(0.0)
    merged["transaction_count"] = merged["transaction_count_actual"].fillna(0).astype(int)
    merged.drop(columns=["consumption_actual", "transaction_count_actual"], inplace=True, errors="ignore")

    return merged.reset_index()


def generate_synthetic_consumption_history(
    sku: str,
    base_stock: int,
    safety_stock: int,
    days_back: int = 30,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates realistic historical demand telemetry when transaction history is young.
    Incorporates weekday velocity and random variance aligned with SKU volume profile.
    """
    rng = np.random.default_rng(abs(hash(sku)) % (2**31 - 1))
    today = datetime.utcnow().date()
    date_index = [today - timedelta(days=days_back - 1 - i) for i in range(days_back)]

    # Estimate expected daily velocity from safety stock magnitude
    typical_daily = max(1.5, safety_stock * 0.18)

    daily_values = []
    for d in date_index:
        weekday = d.weekday()  # 0=Monday, 6=Sunday
        # Business days see higher industrial dispatch velocity
        day_factor = 1.35 if weekday < 5 else 0.4
        val = rng.poisson(lam=max(0.5, typical_daily * day_factor))
        daily_values.append(int(val))

    return pd.DataFrame({
        "date": date_index,
        "consumption": daily_values,
        "transaction_count": [1 if v > 0 else 0 for v in daily_values]
    })


# -----------------------------------------------------------------------------
# 2. Demand Forecasting & Stockout Predictor Models
# -----------------------------------------------------------------------------

def calculate_burn_rate_and_stockout(
    consumption_df: pd.DataFrame,
    current_quantity: int,
    safety_stock: int,
    reorder_point: int,
    lead_time_days: int = 7,
    smoothing_alpha: float = 0.35
) -> Dict[str, Any]:
    """
    Executes Exponential Smoothing (SES) and Linear Trend Estimation to model:
    1. Daily Burn Rate (units/day)
    2. Estimated Days Until Stockout (EDUS)
    3. Exact Recommended Restock Order Quantity
    """
    if consumption_df.empty or "consumption" not in consumption_df.columns:
        burn_rate = 1.0
    else:
        values = consumption_df["consumption"].values
        if len(values) == 0 or np.sum(values) == 0:
            burn_rate = 0.5
        else:
            # 1. Exponential Smoothing (EWMA) gives higher weight to recent velocity
            series = pd.Series(values)
            ewma = series.ewm(alpha=smoothing_alpha, adjust=False).mean()
            recent_ewma_burn = float(ewma.iloc[-1])

            # 2. Linear Trend Estimation (OLS) over the series
            x = np.arange(len(values))
            if len(values) >= 5:
                slope, _ = np.polyfit(x, values, 1)
            else:
                slope = 0.0

            # Combined velocity with slope momentum adjustment
            projected_burn = recent_ewma_burn + (slope * 0.5)
            # Safe non-negative bound
            burn_rate = max(0.1, round(float(projected_burn), 2))

    # Calculate Estimated Days Until Stockout (EDUS)
    if current_quantity <= 0:
        edus = 0.0
    elif burn_rate <= 0:
        edus = 999.0
    else:
        edus = round(current_quantity / burn_rate, 1)

    # Classify Risk Level
    if current_quantity == 0:
        urgency = "STOCKOUT"
        badge_color = "#EF4444"
    elif edus <= 3.0:
        urgency = "CRITICAL"
        badge_color = "#F43F5E"
    elif edus <= lead_time_days:
        urgency = "HIGH"
        badge_color = "#F59E0B"
    elif edus <= (lead_time_days * 2):
        urgency = "MODERATE"
        badge_color = "#3B82F6"
    else:
        urgency = "HEALTHY"
        badge_color = "#10B981"

    # Compute Projected Critical Dates
    today = datetime.utcnow().date()
    stockout_date = today + timedelta(days=math.floor(edus)) if edus < 365 else None

    # Date when inventory crosses safety stock threshold
    units_to_safety = current_quantity - safety_stock
    if units_to_safety <= 0:
        safety_breach_date = today
    elif burn_rate > 0:
        days_to_safety = units_to_safety / burn_rate
        safety_breach_date = today + timedelta(days=math.floor(days_to_safety))
    else:
        safety_breach_date = None

    # Calculate Recommended Replenishment Quantity
    # Policy: Order enough to cover Lead Time + Review Period buffer (7 days) + Safety Stock Deficit
    review_period_days = 7
    lead_time_demand = burn_rate * (lead_time_days + review_period_days)
    target_inventory = lead_time_demand + safety_stock
    
    if current_quantity < target_inventory:
        recommended_order_qty = int(math.ceil(target_inventory - current_quantity))
        # Round up to convenient multiples of 5
        recommended_order_qty = int(math.ceil(recommended_order_qty / 5.0) * 5)
    else:
        recommended_order_qty = 0

    return {
        "daily_burn_rate": burn_rate,
        "estimated_days_until_stockout": edus,
        "urgency_level": urgency,
        "badge_color": badge_color,
        "lead_time_days": lead_time_days,
        "current_quantity": current_quantity,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "recommended_order_quantity": recommended_order_qty,
        "stockout_date": stockout_date,
        "safety_breach_date": safety_breach_date
    }


# -----------------------------------------------------------------------------
# 3. Projected 14-Day Depletion Trajectory
# -----------------------------------------------------------------------------

def generate_14day_depletion_curve(
    current_quantity: int,
    daily_burn_rate: float,
    forecast_days: int = 14
) -> pd.DataFrame:
    """
    Simulates inventory depletion from Day 0 to Day 14 based on projected burn rate.
    """
    today = datetime.utcnow().date()
    records = []
    
    for day_offset in range(forecast_days + 1):
        target_date = today + timedelta(days=day_offset)
        projected_qty = max(0.0, current_quantity - (day_offset * daily_burn_rate))
        records.append({
            "day_offset": day_offset,
            "date": target_date,
            "projected_quantity": round(projected_qty, 1)
        })

    return pd.DataFrame(records)


# -----------------------------------------------------------------------------
# 4. Interactive Plotly Visualizations (Dark Industrial Aesthetic)
# -----------------------------------------------------------------------------

def build_consumption_trend_chart(
    consumption_df: pd.DataFrame,
    product_name: str,
    sku: str
) -> go.Figure:
    """
    Renders 30-day historical consumption bar chart with rolling 7-day velocity line.
    """
    df = consumption_df.copy()
    df["rolling_7d"] = df["consumption"].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()

    # Daily consumption volume bars
    fig.add_trace(go.Bar(
        x=df["date"],
        y=df["consumption"],
        name="Daily Outflow (Units)",
        marker=dict(
            color="rgba(59, 130, 246, 0.65)",
            line=dict(color="#3B82F6", width=1.5)
        ),
        hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Units Dispatched:</b> %{y}<extra></extra>"
    ))

    # 7-day rolling moving average trend line
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["rolling_7d"],
        name="7-Day Moving Avg Velocity",
        mode="lines",
        line=dict(color="#38BDF8", width=2.5, dash="solid"),
        hovertemplate="<b>7D Trend:</b> %{y:.1f} units/day<extra></extra>"
    ))

    fig.update_layout(
        title=f"<b>30-Day Historical Consumption Trend</b><br><span style='font-size:12px; color:#94A3B8;'>{sku} — {product_name}</span>",
        paper_bgcolor="rgba(15, 23, 42, 0)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#F8FAFC"),
        margin=dict(l=40, r=30, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(51, 65, 85, 0.4)",
            linecolor="#334155",
            tickformat="%b %d"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(51, 65, 85, 0.4)",
            linecolor="#334155",
            title="Units Dispatched"
        ),
        hovermode="x unified"
    )

    return fig


def build_depletion_forecast_chart(
    depletion_df: pd.DataFrame,
    reorder_point: int,
    safety_stock: int,
    product_name: str,
    sku: str,
    edus: float
) -> go.Figure:
    """
    Renders 14-day stock depletion curve with horizontal Reorder Point and Safety Stock lines.
    """
    fig = go.Figure()

    # Projected inventory line
    fig.add_trace(go.Scatter(
        x=depletion_df["date"],
        y=depletion_df["projected_quantity"],
        name="Projected Inventory Balance",
        mode="lines+markers",
        line=dict(color="#10B981" if edus > 14 else ("#F59E0B" if edus > 7 else "#EF4444"), width=3),
        marker=dict(size=6, symbol="circle"),
        hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Projected Stock:</b> %{y:.1f} units<extra></extra>"
    ))

    # Reorder Point Reference Line
    fig.add_hline(
        y=reorder_point,
        line_dash="dash",
        line_color="#F59E0B",
        line_width=2,
        annotation_text=f"Reorder Point ({reorder_point} units)",
        annotation_position="top right",
        annotation_font=dict(color="#F59E0B", size=11)
    )

    # Safety Stock Reference Line
    fig.add_hline(
        y=safety_stock,
        line_dash="dot",
        line_color="#EF4444",
        line_width=2,
        annotation_text=f"Safety Stock ({safety_stock} units)",
        annotation_position="bottom right",
        annotation_font=dict(color="#EF4444", size=11)
    )

    fig.update_layout(
        title=f"<b>14-Day Forward Stock Depletion Trajectory</b><br><span style='font-size:12px; color:#94A3B8;'>{sku} — {product_name}</span>",
        paper_bgcolor="rgba(15, 23, 42, 0)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#F8FAFC"),
        margin=dict(l=40, r=30, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(51, 65, 85, 0.4)",
            linecolor="#334155",
            tickformat="%b %d"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(51, 65, 85, 0.4)",
            linecolor="#334155",
            title="Projected On-Hand Units",
            rangemode="tozero"
        ),
        hovermode="x unified"
    )

    return fig
