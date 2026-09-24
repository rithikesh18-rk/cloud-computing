"""
Cloud-Based Multi-Warehouse Inventory Management System
Production Streamlit Application
Architected for Streamlit Community Cloud & Managed MySQL DBaaS.
"""

import os
import math
from datetime import datetime
from typing import Dict, Any, Optional

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.db_handler import (
    get_db_manager,
    get_inventory_summary,
    get_critical_low_stock,
    get_warehouses_list,
    get_products_list,
    get_transactions_ledger,
    get_stock_for_product_warehouse,
    execute_restock,
    execute_dispatch,
    execute_transfer,
    InsufficientStockError,
    ResourceNotFoundError,
    DeadlockRetryExhaustedError,
    DatabaseConstraintViolationError,
    DatabaseTransactionError
)

from utils.forecasting import (
    aggregate_daily_consumption,
    generate_synthetic_consumption_history,
    calculate_burn_rate_and_stockout,
    generate_14day_depletion_curve,
    build_consumption_trend_chart,
    build_depletion_forecast_chart
)

# -----------------------------------------------------------------------------
# 1. Page Configuration & Modern Industrial Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Cloud Inventory Orchestrator",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Modern Industrial Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 98%;
    }

    /* Industrial Dashboard KPI Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(51, 65, 85, 0.7);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, border-color 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.6);
    }

    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3B82F6, #10B981);
    }
    
    .metric-card-alert::before {
        background: linear-gradient(90deg, #EF4444, #F59E0B) !important;
    }

    .metric-label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.2;
    }

    .metric-sub {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Status Badges */
    .badge-out {
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.72rem;
        text-transform: uppercase;
    }

    .badge-warn {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.72rem;
        text-transform: uppercase;
    }

    .badge-healthy {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.72rem;
        text-transform: uppercase;
    }

    /* Operation Panels */
    .op-box {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(51, 65, 85, 0.6);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
    }

    /* Alert Banner */
    .callout-warning {
        background: rgba(245, 158, 11, 0.08);
        border-left: 4px solid #F59E0B;
        border-radius: 4px;
        padding: 12px 16px;
        margin-bottom: 20px;
    }

    /* Transfer Bridge Visual */
    .transfer-bridge {
        background: rgba(30, 41, 59, 0.6);
        border: 1px dashed rgba(59, 130, 246, 0.5);
        border-radius: 10px;
        padding: 16px;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Mock Dataset Fallback Generator (For Instant Local / Preview Demos)
# -----------------------------------------------------------------------------

def build_mock_datasets():
    """Generates high-fidelity mock datasets matching database/seed_data.sql."""
    mock_wh = pd.DataFrame([
        {"id": 1, "name": "Central Logistics Hub (Dallas)", "location": "Dallas, TX", "capacity": 120000},
        {"id": 2, "name": "Pacific Northwest Facility (Seattle)", "location": "Seattle, WA", "capacity": 75000},
        {"id": 3, "name": "Great Lakes Transit Depot (Chicago)", "location": "Chicago, IL", "capacity": 50000},
    ])

    mock_prods = pd.DataFrame([
        {"id": 1, "sku": "FST-HEX-M12-100", "name": "Grade 8.8 M12 Hex Head Bolts (Box of 100)", "category_name": "Industrial Fasteners & Hardware", "unit_price": 42.50, "reorder_point": 60, "safety_stock": 20},
        {"id": 2, "sku": "FST-ANCH-SS-050", "name": "Stainless Steel Wedge Anchor 1/2\"x4\" (Box of 50)", "category_name": "Industrial Fasteners & Hardware", "unit_price": 68.00, "reorder_point": 40, "safety_stock": 15},
        {"id": 3, "sku": "FST-BRKT-HEAVY", "name": "Heavy-Duty Galvanized Structural Angle Bracket 90°", "category_name": "Industrial Fasteners & Hardware", "unit_price": 14.25, "reorder_point": 100, "safety_stock": 30},
        {"id": 4, "sku": "SNS-IOT-TEMP-01", "name": "LoRaWAN Industrial Rugged Temp & Humidity Sensor", "category_name": "Sensors & Automation Controls", "unit_price": 125.00, "reorder_point": 25, "safety_stock": 10},
        {"id": 5, "sku": "SNS-OPT-PROX-24V", "name": "Optical Laser Proximity Sensor 24V DC PNP", "category_name": "Sensors & Automation Controls", "unit_price": 89.50, "reorder_point": 30, "safety_stock": 12},
        {"id": 6, "sku": "SNS-PRESS-TR-10", "name": "Ceramic Pressure Transducer 0-10 Bar 4-20mA", "category_name": "Sensors & Automation Controls", "unit_price": 145.00, "reorder_point": 20, "safety_stock": 8},
        {"id": 7, "sku": "PPE-RESP-N95-FLT", "name": "Dual-Cartridge Half-Facepiece Chemical Respirator", "category_name": "Safety & Personal Protection (PPE)", "unit_price": 34.75, "reorder_point": 50, "safety_stock": 20},
        {"id": 8, "sku": "PPE-GLV-CUT5-PR", "name": "Level 5 Cut-Resistant Kevlar Nitrile Work Gloves", "category_name": "Safety & Personal Protection (PPE)", "unit_price": 12.80, "reorder_point": 120, "safety_stock": 40},
        {"id": 9, "sku": "PPE-HELM-LED-WHT", "name": "ANSI Class E Vented Hard Hat w/ Integrated Headlamp", "category_name": "Safety & Personal Protection (PPE)", "unit_price": 48.90, "reorder_point": 40, "safety_stock": 15},
        {"id": 10, "sku": "PKG-THRM-PAL-CVR", "name": "Insulated Cold-Chain Thermal Pallet Shroud Cover", "category_name": "Thermal & Protective Packaging", "unit_price": 78.00, "reorder_point": 35, "safety_stock": 10},
        {"id": 11, "sku": "PKG-BUBL-BIO-500", "name": "Biodegradable Cushioning Bubble Wrap 500ft Roll", "category_name": "Thermal & Protective Packaging", "unit_price": 38.50, "reorder_point": 45, "safety_stock": 15},
        {"id": 12, "sku": "PKG-PET-STRAP-HD", "name": "High-Tensile Polyester Strapping Coil 5/8\" x 4000ft", "category_name": "Thermal & Protective Packaging", "unit_price": 62.00, "reorder_point": 30, "safety_stock": 10},
        {"id": 13, "sku": "PWR-CBL-4C-100M", "name": "12 AWG 4-Conductor Shielded Tray Cable (100m Drum)", "category_name": "Power Distribution & Cabling", "unit_price": 215.00, "reorder_point": 15, "safety_stock": 5},
        {"id": 14, "sku": "PWR-MCB-3P-063A", "name": "3-Pole 63A 400V DIN Rail Miniature Circuit Breaker", "category_name": "Power Distribution & Cabling", "unit_price": 52.50, "reorder_point": 30, "safety_stock": 10},
        {"id": 15, "sku": "PWR-TRM-DIN-100", "name": "Screw-Clamp DIN Rail Feed-Through Terminal Block (100pk)", "category_name": "Power Distribution & Cabling", "unit_price": 28.00, "reorder_point": 50, "safety_stock": 20},
    ])

    inv_records = []
    quantities = {
        # Dallas (WH 1)
        (1, 1): 450, (2, 1): 280, (3, 1): 620, (4, 1): 95, (5, 1): 80, (6, 1): 4,
        (7, 1): 190, (8, 1): 410, (9, 1): 115, (10, 1): 140, (11, 1): 185, (12, 1): 95,
        (13, 1): 38, (14, 1): 110, (15, 1): 240,
        # Seattle (WH 2)
        (1, 2): 75, (2, 2): 45, (3, 2): 120, (4, 2): 18, (5, 2): 22, (6, 2): 14,
        (7, 2): 38, (8, 2): 85, (9, 2): 12, (10, 2): 42, (11, 2): 18, (12, 2): 8,
        (13, 2): 2, (14, 2): 28, (15, 2): 60,
        # Chicago (WH 3)
        (1, 3): 25, (2, 3): 8, (3, 3): 85, (4, 3): 6, (5, 3): 0, (6, 3): 0,
        (7, 3): 14, (8, 3): 210, (9, 3): 0, (10, 3): 0, (11, 3): 55, (12, 3): 35,
        (13, 3): 19, (14, 3): 9, (15, 3): 15,
    }

    wh_dict = {1: "Central Logistics Hub (Dallas)", 2: "Pacific Northwest Facility (Seattle)", 3: "Great Lakes Transit Depot (Chicago)"}
    
    for (pid, wid), qty in quantities.items():
        p_row = mock_prods[mock_prods["id"] == pid].iloc[0]
        w_name = wh_dict[wid]
        reorder = p_row["reorder_point"]
        safety = p_row["safety_stock"]
        price = p_row["unit_price"]

        if qty == 0:
            status = "OUT_OF_STOCK"
        elif qty <= safety:
            status = "CRITICAL"
        elif qty <= reorder:
            status = "LOW_STOCK"
        else:
            status = "HEALTHY"

        inv_records.append({
            "warehouse_id": wid,
            "warehouse_name": w_name,
            "warehouse_location": "USA",
            "product_id": pid,
            "sku": p_row["sku"],
            "product_name": p_row["name"],
            "category_name": p_row["category_name"],
            "unit_price": price,
            "quantity": qty,
            "reorder_point": reorder,
            "safety_stock": safety,
            "total_valuation": round(qty * price, 2),
            "stock_status": status,
            "updated_at": datetime.utcnow()
        })

    mock_inv = pd.DataFrame(inv_records)
    mock_alerts = mock_inv[mock_inv["stock_status"].isin(["OUT_OF_STOCK", "CRITICAL", "LOW_STOCK"])].copy()
    mock_alerts["suggested_replenishment"] = mock_alerts["reorder_point"] - mock_alerts["quantity"]

    mock_ledger = pd.DataFrame([
        {"id": 16, "created_at": datetime.utcnow(), "transaction_type": "ADJUSTMENT", "change_quantity": -2, "warehouse_name": "Pacific Northwest Facility (Seattle)", "sku": "PKG-PET-STRAP-HD", "product_name": "High-Tensile Polyester Strapping Coil 5/8\" x 4000ft", "category_name": "Thermal & Protective Packaging", "reference_id": "DMG-WRH-2024-03"},
        {"id": 15, "created_at": datetime.utcnow(), "transaction_type": "TRANSFER", "change_quantity": 20, "warehouse_name": "Pacific Northwest Facility (Seattle)", "sku": "PKG-THRM-PAL-CVR", "product_name": "Insulated Cold-Chain Thermal Pallet Shroud Cover", "category_name": "Thermal & Protective Packaging", "reference_id": "TR-DAL-SEA-01 [IN: WH-1]"},
        {"id": 14, "created_at": datetime.utcnow(), "transaction_type": "TRANSFER", "change_quantity": -20, "warehouse_name": "Central Logistics Hub (Dallas)", "sku": "PKG-THRM-PAL-CVR", "product_name": "Insulated Cold-Chain Thermal Pallet Shroud Cover", "category_name": "Thermal & Protective Packaging", "reference_id": "TR-DAL-SEA-01 [OUT: WH-2]"},
        {"id": 13, "created_at": datetime.utcnow(), "transaction_type": "DISPATCH", "change_quantity": -8, "warehouse_name": "Pacific Northwest Facility (Seattle)", "sku": "PWR-CBL-4C-100M", "product_name": "12 AWG 4-Conductor Shielded Tray Cable (100m Drum)", "category_name": "Power Distribution & Cabling", "reference_id": "SO-ORD-90555"},
        {"id": 12, "created_at": datetime.utcnow(), "transaction_type": "DISPATCH", "change_quantity": -46, "warehouse_name": "Central Logistics Hub (Dallas)", "sku": "SNS-PRESS-TR-10", "product_name": "Ceramic Pressure Transducer 0-10 Bar 4-20mA", "category_name": "Sensors & Automation Controls", "reference_id": "SO-ORD-90342"},
        {"id": 11, "created_at": datetime.utcnow(), "transaction_type": "RESTOCK", "change_quantity": 500, "warehouse_name": "Central Logistics Hub (Dallas)", "sku": "FST-HEX-M12-100", "product_name": "Grade 8.8 M12 Hex Head Bolts (Box of 100)", "category_name": "Industrial Fasteners & Hardware", "reference_id": "PO-2024-8801"}
    ])

    return mock_wh, mock_prods, mock_inv, mock_alerts, mock_ledger


# -----------------------------------------------------------------------------
# 3. Cached Data Fetchers (Zero-Flicker Architecture)
# -----------------------------------------------------------------------------

@st.cache_data(ttl=20, show_spinner=False)
def fetch_inventory_cached() -> pd.DataFrame:
    try:
        return get_inventory_summary()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=20, show_spinner=False)
def fetch_alerts_cached() -> pd.DataFrame:
    try:
        return get_critical_low_stock()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60, show_spinner=False)
def fetch_warehouses_cached() -> pd.DataFrame:
    try:
        return get_warehouses_list()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60, show_spinner=False)
def fetch_products_cached() -> pd.DataFrame:
    try:
        return get_products_list()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=15, show_spinner=False)
def fetch_ledger_cached(limit: int = 500) -> pd.DataFrame:
    try:
        return get_transactions_ledger(limit=limit)
    except Exception:
        return pd.DataFrame()

def invalidate_all_inventory_caches():
    st.cache_data.clear()


# -----------------------------------------------------------------------------
# 4. Connection Status & Data Resolution
# -----------------------------------------------------------------------------

db_health = get_db_manager().check_health()
is_db_connected = db_health.get("status") == "healthy"

if is_db_connected:
    df_inv = fetch_inventory_cached()
    df_alerts = fetch_alerts_cached()
    df_warehouses = fetch_warehouses_cached()
    df_products = fetch_products_cached()
    df_ledger = fetch_ledger_cached()
    is_mock_active = False
else:
    m_wh, m_prods, m_inv, m_alerts, m_ledger = build_mock_datasets()
    df_inv = m_inv
    df_alerts = m_alerts
    df_warehouses = m_wh
    df_products = m_prods
    df_ledger = m_ledger
    is_mock_active = True


# -----------------------------------------------------------------------------
# 5. Sidebar: Connection Status & Quick Controls
# -----------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🏢 Multi-Warehouse Cloud")
    st.caption("Engineered for MySQL DBaaS & Streamlit Cloud")
    st.divider()

    if is_db_connected:
        st.success(f"🟢 **DB Connected**\n`MySQL {db_health.get('version', '')}`")
        st.caption(f"Database: `{db_health.get('database', 'inventory_db')}`")
    else:
        st.warning("🟡 **Demo Mode (Mock DB)**")
        st.caption("Displaying seed dataset. Connect your managed MySQL instance to persist live writes.")
        with st.expander("DBaaS Setup Instructions"):
            st.markdown("""
            1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
            2. Fill in your DBaaS `host`, `user`, and `password`.
            3. Apply `database/schema.sql` and `database/seed_data.sql`.
            """)

    st.divider()
    st.markdown("#### ⚙️ Quick Actions")
    if st.button("🔄 Refresh Data Cache", use_container_width=True):
        invalidate_all_inventory_caches()
        st.toast("Data cache invalidated!", icon="🧹")
        st.rerun()

    st.divider()
    st.caption(f"UTC Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("Architecture: ACID · InnoDB · QueuePool")


# -----------------------------------------------------------------------------
# 6. Global Header & High-Level KPI Summary Cards
# -----------------------------------------------------------------------------

st.title("📦 Multi-Warehouse Inventory Management System")
st.markdown("Real-time distributed supply chain orchestration, predictive demand analytics, and audit tracking.")

# Compute High-Impact KPI Metrics
total_valuation = df_inv["total_valuation"].sum() if not df_inv.empty else 0.0
total_items = df_inv["quantity"].sum() if not df_inv.empty else 0
active_warehouses_count = df_inv["warehouse_id"].nunique() if not df_inv.empty else len(df_warehouses)
critical_alerts_count = len(df_alerts) if not df_alerts.empty else 0
out_of_stock_count = len(df_alerts[df_alerts["stock_status"] == "OUT_OF_STOCK"]) if not df_alerts.empty else 0

# Render Sleek Industrial KPI Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Stock Valuation</div>
        <div class="metric-value">${total_valuation:,.2f}</div>
        <div class="metric-sub">Asset holding across {active_warehouses_count} facilities</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Physical Units</div>
        <div class="metric-value">{total_items:,}</div>
        <div class="metric-sub">Across {len(df_products)} registered catalog SKUs</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Active Facilities</div>
        <div class="metric-value">{active_warehouses_count}</div>
        <div class="metric-sub">Multi-regional distribution network</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    alert_card_class = "metric-card metric-card-alert" if critical_alerts_count > 0 else "metric-card"
    st.markdown(f"""
    <div class="{alert_card_class}">
        <div class="metric-label">Low Stock Alerts</div>
        <div class="metric-value" style="color: {'#F87171' if critical_alerts_count > 0 else '#34D399'};">
            {critical_alerts_count}
        </div>
        <div class="metric-sub">
            {f'<span class="badge-out">{out_of_stock_count} Out of Stock</span>' if out_of_stock_count > 0 else 'All thresholds satisfied'}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 7. Primary Application Navigation Tabs
# -----------------------------------------------------------------------------

tab_overview, tab_operations, tab_transfers, tab_forecasting, tab_ledger = st.tabs([
    "📊 Real-Time Inventory Overview",
    "⚡ Stock Operations (Inbound / Outbound)",
    "🔄 Inter-Warehouse Transfers",
    "📈 Demand Analytics & Stockout Predictor",
    "📜 Audit & Transaction Ledger"
])


# =============================================================================
# TAB 1: Real-Time Inventory Overview
# =============================================================================
with tab_overview:
    st.subheader("Multi-Facility Stock Catalog")
    st.caption("Live on-hand inventory levels, unit prices, total valuations, and threshold tracking.")

    # High-Priority Alert Banner if Shortages Exist
    if not df_alerts.empty:
        crit_skus = df_alerts[df_alerts["stock_status"].isin(["OUT_OF_STOCK", "CRITICAL"])]["sku"].tolist()
        st.markdown(f"""
        <div class="callout-warning">
            <strong>⚠️ Immediate Replenishment Required:</strong> Found <strong>{len(df_alerts)} item instances</strong> at or below safety reorder threshold! 
            Urgent SKUs: <code>{', '.join(crit_skus[:5])}</code>{' ...' if len(crit_skus) > 5 else ''}.
        </div>
        """, unsafe_allow_html=True)

    if not df_inv.empty:
        # Search & Filter Controls
        f1, f2, f3, f4 = st.columns([1.5, 1, 1, 1])
        search_query = f1.text_input("🔍 Search SKU or Product Name", placeholder="e.g. FST-HEX, Sensor, Cable...")

        wh_list = ["All Facilities"] + sorted(df_inv["warehouse_name"].unique().tolist())
        selected_wh = f2.selectbox("Filter Warehouse", wh_list)

        cat_list = ["All Categories"] + sorted(df_inv["category_name"].unique().tolist())
        selected_cat = f3.selectbox("Filter Category", cat_list)

        status_options = ["All Statuses", "Shortages Only (Out/Critical/Low)", "Healthy Only"]
        selected_status = f4.selectbox("Stock Health", status_options)

        # Apply Filters
        filtered = df_inv.copy()

        if search_query.strip():
            sq = search_query.strip().lower()
            filtered = filtered[
                filtered["sku"].str.lower().str.contains(sq) |
                filtered["product_name"].str.lower().str.contains(sq)
            ]

        if selected_wh != "All Facilities":
            filtered = filtered[filtered["warehouse_name"] == selected_wh]

        if selected_cat != "All Categories":
            filtered = filtered[filtered["category_name"] == selected_cat]

        if selected_status == "Shortages Only (Out/Critical/Low)":
            filtered = filtered[filtered["stock_status"].isin(["OUT_OF_STOCK", "CRITICAL", "LOW_STOCK"])]
        elif selected_status == "Healthy Only":
            filtered = filtered[filtered["stock_status"] == "HEALTHY"]

        # Status Icon Mapping for Clean Table Rendering
        def format_status_badge(val):
            if val == "OUT_OF_STOCK":
                return "🔴 Out of Stock"
            elif val == "CRITICAL":
                return "🚨 Critical Shortage"
            elif val == "LOW_STOCK":
                return "⚠️ Low Stock Warning"
            return "🟢 Healthy"

        display_df = filtered.copy()
        display_df["Alert Status"] = display_df["stock_status"].apply(format_status_badge)

        table_cols = [
            "Alert Status", "warehouse_name", "sku", "product_name", 
            "category_name", "quantity", "reorder_point", "safety_stock", 
            "unit_price", "total_valuation", "updated_at"
        ]

        st.dataframe(
            display_df[table_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Alert Status": st.column_config.TextColumn("Health Status", width="medium"),
                "warehouse_name": st.column_config.TextColumn("Facility", width="medium"),
                "sku": st.column_config.TextColumn("SKU Code", width="small"),
                "product_name": st.column_config.TextColumn("Product Name", width="large"),
                "category_name": st.column_config.TextColumn("Category"),
                "quantity": st.column_config.NumberColumn("On-Hand Qty", format="%d"),
                "reorder_point": st.column_config.NumberColumn("Reorder Pt", format="%d"),
                "safety_stock": st.column_config.NumberColumn("Safety Stk", format="%d"),
                "unit_price": st.column_config.NumberColumn("Unit Price ($)", format="$%.2f"),
                "total_valuation": st.column_config.NumberColumn("Total Valuation ($)", format="$%.2f"),
                "updated_at": st.column_config.DatetimeColumn("Last Balance Update", format="YYYY-MM-DD HH:mm")
            }
        )

        st.caption(f"Showing {len(display_df)} matching inventory records out of {len(df_inv)} total balances.")
    else:
        st.info("No inventory records found.")


# =============================================================================
# TAB 2: Stock Operations (Inbound vs Outbound Split Screen)
# =============================================================================
with tab_operations:
    st.subheader("⚡ Stock Movement Operations")
    st.caption("ACID-compliant inventory transactions with exclusive row-level locking (`SELECT ... FOR UPDATE`).")

    if not df_warehouses.empty and not df_products.empty:
        wh_options = {row["name"]: row["id"] for _, row in df_warehouses.iterrows()}
        prod_options = {f"{row['sku']} - {row['name']} ({row['category_name']})": row["id"] for _, row in df_products.iterrows()}

        col_inbound, col_outbound = st.columns(2, gap="large")

        # LEFT COLUMN: Inbound Receiving & Restock
        with col_inbound:
            st.markdown("""
            <div class="op-box">
                <h4 style="margin-top:0; color:#38BDF8;">📥 Inbound Receiving & Restock</h4>
                <p style="color:#94A3B8; font-size:0.85rem; margin-bottom:0;">Record incoming shipments from suppliers, purchase orders, or returns.</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("inbound_restock_form", clear_on_submit=True):
                r_wh_name = st.selectbox("Target Warehouse", list(wh_options.keys()), key="in_wh")
                r_prod_label = st.selectbox("Product SKU to Restock", list(prod_options.keys()), key="in_prod")
                
                selected_prod_id = prod_options[r_prod_label]
                selected_wh_id = wh_options[r_wh_name]
                
                # Live Preview of Current Stock
                if is_db_connected:
                    current_stock_info = get_stock_for_product_warehouse(selected_prod_id, selected_wh_id)
                else:
                    current_stock_info = {"quantity": 45, "status": "HEALTHY"}

                st.caption(f"Current On-Hand in `{r_wh_name}`: **{current_stock_info['quantity']} units** (Status: `{current_stock_info['status']}`)")

                r_qty = st.number_input("Restock Quantity (Units)", min_value=1, max_value=100000, value=50, step=1)
                r_notes = st.text_input("PO / Shipment Reference ID", placeholder="e.g. PO-2024-8801, BOL-77492")
                
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                submit_restock = st.form_submit_button("📥 Post Inbound Restock", use_container_width=True)

                if submit_restock:
                    if is_db_connected:
                        try:
                            res = execute_restock(
                                product_id=selected_prod_id,
                                warehouse_id=selected_wh_id,
                                quantity=r_qty,
                                notes=r_notes or None
                            )
                            invalidate_all_inventory_caches()
                            st.toast(f"Restocked +{r_qty} units of {res['sku']}!", icon="✅")
                            st.success(
                                f"Restock confirmed! Added **{r_qty} units** to `{r_wh_name}`. "
                                f"New balance: **{res['new_balance']} units** (Txn Ref: `{res['reference_id']}`)."
                            )
                        except Exception as ex:
                            st.error(f"Restock transaction failed: {ex}")
                    else:
                        st.toast(f"[Demo Mode] Restocked +{r_qty} units!", icon="✅")
                        st.success(f"[Demo Mode] Successfully posted Restock of **{r_qty} units** for reference `{r_notes or 'PO-DEMO-001'}`.")

        # RIGHT COLUMN: Outbound Fulfillment & Dispatch
        with col_outbound:
            st.markdown("""
            <div class="op-box">
                <h4 style="margin-top:0; color:#F43F5E;">📤 Outbound Order Fulfillment (Dispatch)</h4>
                <p style="color:#94A3B8; font-size:0.85rem; margin-bottom:0;">Fulfill customer sales orders with strict row-locking and deficit protection.</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("outbound_dispatch_form", clear_on_submit=True):
                d_wh_name = st.selectbox("Fulfillment Warehouse", list(wh_options.keys()), key="out_wh")
                d_prod_label = st.selectbox("Product SKU to Dispatch", list(prod_options.keys()), key="out_prod")

                disp_prod_id = prod_options[d_prod_label]
                disp_wh_id = wh_options[d_wh_name]

                # Live Availability Check
                if is_db_connected:
                    disp_stock_info = get_stock_for_product_warehouse(disp_prod_id, disp_wh_id)
                else:
                    disp_stock_info = {"quantity": 18, "reorder_point": 25}

                avail_qty = disp_stock_info["quantity"]
                
                if avail_qty == 0:
                    st.markdown("<span class='badge-out'>⚠️ ZERO STOCK AVAILABLE AT THIS FACILITY</span>", unsafe_allow_html=True)
                elif avail_qty <= disp_stock_info.get("reorder_point", 10):
                    st.markdown(f"<span class='badge-warn'>Low Stock Warning: Only {avail_qty} units on hand</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='badge-healthy'>🟢 On-Hand: {avail_qty} units ready for fulfillment</span>", unsafe_allow_html=True)

                d_qty = st.number_input("Order Dispatch Quantity", min_value=1, max_value=50000, value=10, step=1)
                d_ref = st.text_input("Customer Order / Sales Invoice Ref", placeholder="e.g. SO-ORD-90210, RMA-331")

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                submit_dispatch = st.form_submit_button("📤 Confirm Order Dispatch", use_container_width=True)

                if submit_dispatch:
                    if not d_ref.strip():
                        st.error("Please enter a valid Sales Order / Invoice Reference ID.")
                    elif is_db_connected:
                        try:
                            res = execute_dispatch(
                                product_id=disp_prod_id,
                                warehouse_id=disp_wh_id,
                                quantity=d_qty,
                                order_ref=d_ref.strip()
                            )
                            invalidate_all_inventory_caches()
                            st.toast(f"Dispatched -{d_qty} units of {res['sku']}!", icon="📦")
                            st.success(
                                f"Dispatch completed! Deducted **{d_qty} units** from `{d_wh_name}`. "
                                f"Remaining balance: **{res['remaining_balance']} units** (Ref: `{res['reference_id']}`)."
                            )
                        except InsufficientStockError as ise:
                            st.error(f"⛔ **TRANSACTION REJECTED: INSUFFICIENT STOCK**\n\n{ise}")
                        except Exception as ex:
                            st.error(f"Dispatch transaction failed: {ex}")
                    else:
                        if d_qty > avail_qty:
                            st.error(f"⛔ **TRANSACTION REJECTED: INSUFFICIENT STOCK**\n\nAvailable: {avail_qty}, Requested: {d_qty}")
                        else:
                            st.toast(f"[Demo Mode] Dispatched -{d_qty} units!", icon="📦")
                            st.success(f"[Demo Mode] Successfully dispatched **{d_qty} units** under ref `{d_ref.strip()}`.")
    else:
        st.warning("Warehouse and product master catalogs not found.")


# =============================================================================
# TAB 3: Inter-Warehouse Transfers
# =============================================================================
with tab_transfers:
    st.subheader("🔄 Inter-Warehouse Inventory Relocation")
    st.caption("Rebalance regional stock between facilities with atomic, deadlock-free two-phase locking.")

    if not df_warehouses.empty and not df_products.empty:
        wh_options = {row["name"]: row["id"] for _, row in df_warehouses.iterrows()}
        prod_options = {f"{row['sku']} - {row['name']}": row["id"] for _, row in df_products.iterrows()}

        with st.form("transfer_form"):
            t_prod_label = st.selectbox("Select Product to Relocate", list(prod_options.keys()))
            t_prod_id = prod_options[t_prod_label]

            col_from, col_to = st.columns(2)
            with col_from:
                from_wh_name = st.selectbox("Origin Warehouse (Source)", list(wh_options.keys()), index=0)
            with col_to:
                to_wh_name = st.selectbox("Destination Warehouse (Target)", list(wh_options.keys()), index=min(1, len(wh_options)-1))

            from_wh_id = wh_options[from_wh_name]
            to_wh_id = wh_options[to_wh_name]

            # Live Source & Destination Previews
            if is_db_connected:
                from_stock = get_stock_for_product_warehouse(t_prod_id, from_wh_id)
                to_stock = get_stock_for_product_warehouse(t_prod_id, to_wh_id)
            else:
                from_stock = {"quantity": 140}
                to_stock = {"quantity": 18}

            t_qty = st.number_input("Units to Transfer", min_value=1, max_value=max(1, from_stock["quantity"]), value=min(10, max(1, from_stock["quantity"])), step=1)
            t_ref = st.text_input("Transfer Ticket / Manifest ID", placeholder="e.g. TR-DAL-SEA-01, MTR-8812")

            # Transfer Route Visualizer
            st.markdown(f"""
            <div class="transfer-bridge">
                <strong>Transfer Route Preview:</strong><br>
                <code>{from_wh_name}</code> (Current: {from_stock['quantity']} units) 
                &nbsp; ➡️ &nbsp; <strong>[{t_qty} units]</strong> &nbsp; ➡️ &nbsp; 
                <code>{to_wh_name}</code> (Current: {to_stock['quantity']} units)<br>
                <small style="color:#94A3B8;">Projected Source: {from_stock['quantity'] - t_qty} units | Projected Target: {to_stock['quantity'] + t_qty} units</small>
            </div>
            """, unsafe_allow_html=True)

            execute_transfer_btn = st.form_submit_button("🚀 Execute Atomic Transfer", use_container_width=True)

            if execute_transfer_btn:
                if from_wh_id == to_wh_id:
                    st.error("Origin and Destination facilities must be different.")
                elif is_db_connected:
                    try:
                        res = execute_transfer(
                            product_id=t_prod_id,
                            from_warehouse_id=from_wh_id,
                            to_warehouse_id=to_wh_id,
                            quantity=t_qty,
                            transfer_ref=t_ref or None
                        )
                        invalidate_all_inventory_caches()
                        st.toast(f"Relocated {t_qty} units to {to_wh_name}!", icon="🚚")
                        st.success(
                            f"Transfer verified and recorded! Relocated **{t_qty} units** of `{res['sku']}`.<br>"
                            f"• Source (`{from_wh_name}`) remaining: **{res['source_remaining_balance']} units**<br>"
                            f"• Destination (`{to_wh_name}`) new total: **{res['destination_new_balance']} units**<br>"
                            f"• Transfer Batch ID: `#{res['reference_id']}`"
                        )
                    except InsufficientStockError as ise:
                        st.error(f"⛔ **TRANSFER CANCELLED: SOURCE HAS INSUFFICIENT STOCK**\n\n{ise}")
                    except Exception as ex:
                        st.error(f"Transfer failed: {ex}")
                else:
                    st.toast(f"[Demo Mode] Relocated {t_qty} units!", icon="🚚")
                    st.success(
                        f"[Demo Mode] Relocated **{t_qty} units** from `{from_wh_name}` to `{to_wh_name}`.<br>"
                        f"• Source balance: {from_stock['quantity'] - t_qty} units | Destination balance: {to_stock['quantity'] + t_qty} units"
                    )
    else:
        st.warning("Master warehouse catalog not found.")


# =============================================================================
# TAB 4: Demand Analytics & Stockout Predictor
# =============================================================================
with tab_forecasting:
    st.subheader("📈 Demand Analytics & Stockout Predictor")
    st.caption("Exponential smoothing, daily consumption trends, burn rates, and replenishment recommendations.")

    if not df_products.empty and not df_inv.empty:
        # Forecast Filters & Controls
        fc1, fc2, fc3 = st.columns([1, 1.5, 1])

        wh_fc_options = ["All Facilities (Aggregated Network)"] + sorted(df_warehouses["name"].unique().tolist())
        selected_fc_wh = fc1.selectbox("Forecast Facility", wh_fc_options, key="fc_wh")

        prod_fc_options = {f"{row['sku']} - {row['name']}": row["id"] for _, row in df_products.iterrows()}
        selected_fc_prod_label = fc2.selectbox("Target Product", list(prod_fc_options.keys()), key="fc_prod")
        selected_fc_prod_id = prod_fc_options[selected_fc_prod_label]

        lead_time_days = fc3.slider(
            "Supplier Lead Time (Days)",
            min_value=1,
            max_value=30,
            value=7,
            step=1,
            help="Expected turnaround days from purchase order placement to inventory receiving."
        )

        # Extract selected product parameters
        prod_meta = df_products[df_products["id"] == selected_fc_prod_id].iloc[0]
        sku_code = prod_meta["sku"]
        product_name = prod_meta["name"]
        unit_price = float(prod_meta["unit_price"])
        safety_stock = int(prod_meta["safety_stock"])
        reorder_point = int(prod_meta["reorder_point"])

        # Determine effective current stock and safety thresholds
        if selected_fc_wh == "All Facilities (Aggregated Network)":
            current_qty = int(df_inv[df_inv["product_id"] == selected_fc_prod_id]["quantity"].sum())
            total_safety = safety_stock * len(df_warehouses)
            total_reorder = reorder_point * len(df_warehouses)
            wh_filter_id = None
        else:
            wh_filter_id = df_warehouses[df_warehouses["name"] == selected_fc_wh]["id"].iloc[0]
            prod_wh_inv = df_inv[(df_inv["product_id"] == selected_fc_prod_id) & (df_inv["warehouse_id"] == wh_filter_id)]
            current_qty = int(prod_wh_inv["quantity"].sum()) if not prod_wh_inv.empty else 0
            total_safety = safety_stock
            total_reorder = reorder_point

        # 1. Fetch or synthesize daily consumption time-series
        daily_cons_df = aggregate_daily_consumption(
            transactions_df=df_ledger,
            product_id=selected_fc_prod_id,
            warehouse_id=wh_filter_id,
            days_back=30
        )

        # If historical dispatch records are sparse, use high-fidelity SKU synthetic velocity
        if daily_cons_df["consumption"].sum() < 5:
            daily_cons_df = generate_synthetic_consumption_history(
                sku=sku_code,
                base_stock=current_qty,
                safety_stock=total_safety,
                days_back=30
            )

        # 2. Run Forecasting Model (Burn rate, EDUS, replenishment)
        forecast_metrics = calculate_burn_rate_and_stockout(
            consumption_df=daily_cons_df,
            current_quantity=current_qty,
            safety_stock=total_safety,
            reorder_point=total_reorder,
            lead_time_days=lead_time_days
        )

        burn_rate = forecast_metrics["daily_burn_rate"]
        edus = forecast_metrics["estimated_days_until_stockout"]
        urgency = forecast_metrics["urgency_level"]
        rec_order_qty = forecast_metrics["recommended_order_quantity"]
        stockout_dt = forecast_metrics["stockout_date"]
        safety_breach_dt = forecast_metrics["safety_breach_date"]

        # Top Executive Predictor KPI Cards
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Daily Burn Rate</div>
                <div class="metric-value">{burn_rate:.2f} <span style="font-size:1rem; color:#94A3B8;">units/day</span></div>
                <div class="metric-sub">EWMA smoothed consumption</div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            urgency_colors = {
                "STOCKOUT": ("#EF4444", "🔴 ZERO STOCK"),
                "CRITICAL": ("#F43F5E", "🚨 CRITICAL (<3d)"),
                "HIGH": ("#F59E0B", "⚠️ HIGH RISK (<LeadTime)"),
                "MODERATE": ("#3B82F6", "🔵 MODERATE"),
                "HEALTHY": ("#10B981", "🟢 HEALTHY (>2x L)")
            }
            u_color, u_label = urgency_colors.get(urgency, ("#94A3B8", urgency))
            edus_display = f"{edus:.1f} Days" if edus < 365 else "365+ Days"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Estimated Days to Stockout</div>
                <div class="metric-value" style="color: {u_color};">{edus_display}</div>
                <div class="metric-sub"><span style="color:{u_color}; font-weight:700;">{u_label}</span></div>
            </div>
            """, unsafe_allow_html=True)

        with m3:
            order_val = rec_order_qty * unit_price
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Recommended Reorder PO</div>
                <div class="metric-value">{rec_order_qty:,} <span style="font-size:1rem; color:#94A3B8;">units</span></div>
                <div class="metric-sub">Est. Cost: ${order_val:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with m4:
            stockout_str = stockout_dt.strftime("%b %d, %Y") if stockout_dt else "No Immediate Risk"
            breach_str = safety_breach_dt.strftime("%b %d") if safety_breach_dt else "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Projected Stockout Date</div>
                <div class="metric-value" style="font-size:1.45rem;">{stockout_str}</div>
                <div class="metric-sub">Safety Threshold Breach: {breach_str}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Plotly Charts: Consumption Trend & Depletion Curve
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig_trend = build_consumption_trend_chart(
                consumption_df=daily_cons_df,
                product_name=product_name,
                sku=sku_code
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        with chart_col2:
            depletion_df = generate_14day_depletion_curve(
                current_quantity=current_qty,
                daily_burn_rate=burn_rate,
                forecast_days=14
            )
            fig_depletion = build_depletion_forecast_chart(
                depletion_df=depletion_df,
                reorder_point=total_reorder,
                safety_stock=total_safety,
                product_name=product_name,
                sku=sku_code,
                edus=edus
            )
            st.plotly_chart(fig_depletion, use_container_width=True)

        # Enterprise Multi-SKU Predictive Risk Matrix
        st.markdown("---")
        st.subheader("🎯 Enterprise Multi-SKU Depletion & Reorder Matrix")
        st.caption("Automated scan of all catalog items ranked by days until stockout.")

        matrix_rows = []
        for _, p_item in df_products.iterrows():
            pid = p_item["id"]
            p_sku = p_item["sku"]
            p_name = p_item["name"]
            p_cat = p_item["category_name"]
            p_price = float(p_item["unit_price"])
            p_safety = int(p_item["safety_stock"])
            p_reorder = int(p_item["reorder_point"])

            if selected_fc_wh == "All Facilities (Aggregated Network)":
                p_qty = int(df_inv[df_inv["product_id"] == pid]["quantity"].sum())
                eff_safety = p_safety * len(df_warehouses)
                eff_reorder = p_reorder * len(df_warehouses)
            else:
                p_inv_sub = df_inv[(df_inv["product_id"] == pid) & (df_inv["warehouse_id"] == wh_filter_id)]
                p_qty = int(p_inv_sub["quantity"].sum()) if not p_inv_sub.empty else 0
                eff_safety = p_safety
                eff_reorder = p_reorder

            # Dynamic velocity approximation for portfolio scan
            approx_burn = max(0.2, eff_safety * 0.15)
            p_edus = round(p_qty / approx_burn, 1) if p_qty > 0 else 0.0

            if p_qty == 0:
                p_urgency = "🔴 Stockout"
            elif p_edus <= 3:
                p_urgency = "🚨 Critical (<3d)"
            elif p_edus <= lead_time_days:
                p_urgency = "⚠️ High Risk"
            elif p_edus <= lead_time_days * 2:
                p_urgency = "🔵 Moderate"
            else:
                p_urgency = "🟢 Healthy"

            target_hold = (approx_burn * (lead_time_days + 7)) + eff_safety
            rec_po = max(0, int(math.ceil((target_hold - p_qty) / 5.0) * 5))

            matrix_rows.append({
                "Urgency": p_urgency,
                "SKU": p_sku,
                "Product Description": p_name,
                "Category": p_cat,
                "On-Hand Qty": p_qty,
                "Burn Rate (u/d)": round(approx_burn, 2),
                "Days to Stockout": p_edus,
                "Recommended PO": rec_po,
                "Unit Price ($)": p_price,
                "Order Est. Value ($)": round(rec_po * p_price, 2)
            })

        matrix_df = pd.DataFrame(matrix_rows).sort_values("Days to Stockout", ascending=True)

        st.dataframe(
            matrix_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Urgency": st.column_config.TextColumn("Risk Tier"),
                "On-Hand Qty": st.column_config.NumberColumn("Current Qty", format="%d"),
                "Burn Rate (u/d)": st.column_config.NumberColumn("Velocity (u/day)", format="%.2f"),
                "Days to Stockout": st.column_config.NumberColumn("EDUS (Days)", format="%.1f"),
                "Recommended PO": st.column_config.NumberColumn("Suggested PO (Units)", format="%d"),
                "Unit Price ($)": st.column_config.NumberColumn("Unit Price", format="$%.2f"),
                "Order Est. Value ($)": st.column_config.NumberColumn("Total PO Value", format="$%.2f")
            }
        )
    else:
        st.info("Product catalog empty. Connect database to enable predictive analytics.")


# =============================================================================
# TAB 5: Audit & Transaction Ledger
# =============================================================================
with tab_ledger:
    st.subheader("📜 Immutable Supply Chain Audit Ledger")
    st.caption("Immutable append-only log of every RESTOCK, DISPATCH, TRANSFER, and ADJUSTMENT event.")

    if not df_ledger.empty:
        # Search & Filter Controls
        l1, l2, l3 = st.columns([1.5, 1, 1])
        ledger_search = l1.text_input("🔍 Search Reference / SKU / Product", placeholder="e.g. PO-2024, SO-ORD, TR-...")

        all_types = ["All Types"] + sorted(df_ledger["transaction_type"].unique().tolist())
        selected_type = l2.selectbox("Filter Transaction Type", all_types)

        all_whs = ["All Facilities"] + sorted(df_ledger["warehouse_name"].unique().tolist())
        selected_ledger_wh = l3.selectbox("Filter Warehouse", all_whs, key="ledg_wh")

        # Apply Filters
        filtered_ledger = df_ledger.copy()
        if ledger_search.strip():
            lq = ledger_search.strip().lower()
            filtered_ledger = filtered_ledger[
                filtered_ledger["reference_id"].astype(str).str.lower().str.contains(lq) |
                filtered_ledger["sku"].str.lower().str.contains(lq) |
                filtered_ledger["product_name"].str.lower().str.contains(lq)
            ]

        if selected_type != "All Types":
            filtered_ledger = filtered_ledger[filtered_ledger["transaction_type"] == selected_type]

        if selected_ledger_wh != "All Facilities":
            filtered_ledger = filtered_ledger[filtered_ledger["warehouse_name"] == selected_ledger_wh]

        # Top Ledger Activity Metrics
        total_inbound = filtered_ledger[filtered_ledger["change_quantity"] > 0]["change_quantity"].sum()
        total_outbound = abs(filtered_ledger[filtered_ledger["change_quantity"] < 0]["change_quantity"].sum())
        total_events = len(filtered_ledger)

        lm1, lm2, lm3 = st.columns(3)
        lm1.metric("Logged Transactions", f"{total_events:,}")
        lm2.metric("Total Inbound Received", f"+{total_inbound:,} units")
        lm3.metric("Total Outbound Dispatched", f"-{total_outbound:,} units")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Export to CSV Button
        csv_data = filtered_ledger.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Ledger to CSV",
            data=csv_data,
            file_name=f"inventory_audit_ledger_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=False
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Dataframe Display
        st.dataframe(
            filtered_ledger[[
                "id", "created_at", "transaction_type", "change_quantity", 
                "warehouse_name", "sku", "product_name", "category_name", "reference_id"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("Txn ID", format="%d", width="small"),
                "created_at": st.column_config.DatetimeColumn("Recorded Timestamp", format="YYYY-MM-DD HH:mm:ss"),
                "transaction_type": st.column_config.TextColumn("Movement Type"),
                "change_quantity": st.column_config.NumberColumn("Quantity Delta", format="%+d"),
                "warehouse_name": st.column_config.TextColumn("Facility"),
                "sku": st.column_config.TextColumn("SKU Code"),
                "product_name": st.column_config.TextColumn("Item Description"),
                "category_name": st.column_config.TextColumn("Category"),
                "reference_id": st.column_config.TextColumn("Manifest / Ref ID")
            }
        )
    else:
        st.info("No transaction ledger entries recorded yet.")
