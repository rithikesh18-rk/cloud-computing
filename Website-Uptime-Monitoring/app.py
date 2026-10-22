"""
Cloud Website Uptime & Endpoint Reliability Monitor - Dual-Mode Dashboard & UI
-----------------------------------------------------------------------------
Interactive Streamlit visualization portal and terminal CLI health auditor.
Tracks real-time uptime, SLA percentages, SSL certificate lifecycles,
latency curves, and incident history.
"""

import os
import sys
import sqlite3
from datetime import datetime, timezone, timedelta
import pandas as pd

# Core checker imports
from checker import (
    DB_PATH,
    ENDPOINTS_FILE,
    ALERT_LOG_PATH,
    UPTIME_LOG_PATH,
    init_db,
    seed_synthetic_history_if_needed,
    load_endpoints,
    probe_endpoint,
    record_check_result,
    calculate_sla,
    run_single_sweep,
)


def is_running_streamlit():
    """Detect whether app.py was launched via Streamlit CLI."""
    if any("streamlit" in arg.lower() for arg in sys.argv[:2]):
        return True
    if os.environ.get("STREAMLIT_SERVER_PORT") or os.environ.get("STREAMLIT_SERVER_ADDRESS"):
        return True
    return False


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def load_dashboard_data():
    conn = get_db_connection()
    init_db()
    seed_synthetic_history_if_needed(conn)

    # Health checks dataframe
    checks_df = pd.read_sql_query("""
        SELECT
            hc.id,
            hc.endpoint_id,
            ep.name as endpoint_name,
            ep.url,
            hc.timestamp,
            hc.status_code,
            hc.response_time_ms,
            hc.status,
            hc.ssl_valid,
            hc.ssl_days_left,
            hc.ssl_issuer,
            hc.error_message
        FROM health_checks hc
        JOIN endpoints ep ON hc.endpoint_id = ep.id
        ORDER BY hc.id DESC
    """, conn)

    # Incidents dataframe
    incidents_df = pd.read_sql_query("""
        SELECT
            id,
            endpoint_name,
            started_at,
            resolved_at,
            duration_seconds,
            status,
            root_cause
        FROM incidents
        ORDER BY id DESC
    """, conn)

    # Alerts dataframe
    alerts_df = pd.read_sql_query("""
        SELECT
            id,
            endpoint_id,
            timestamp,
            alert_type,
            channel,
            message,
            status
        FROM alerts
        ORDER BY id DESC
    """, conn)

    # Latest status per endpoint
    latest_df = checks_df.sort_values("timestamp").groupby("endpoint_id").last().reset_index()

    conn.close()
    return checks_df, incidents_df, alerts_df, latest_df


def render_streamlit_dashboard():
    import streamlit as st
    import plotly.express as px

    st.set_page_config(
        page_title="Cloud Website Uptime Monitor",
        page_icon="🟢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom styling
    st.markdown("""
        <style>
        .metric-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        .status-up {
            color: #2ea043;
            font-weight: 700;
        }
        .status-deg {
            color: #d29922;
            font-weight: 700;
        }
        .status-down {
            color: #f85149;
            font-weight: 700;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🌐 Cloud Website Uptime & Endpoint Reliability Monitor")
    st.caption("Automated Multi-Endpoint Health Poller • SLA Availability Tracker • SSL Expiry Watchdog • Incident Alerting")

    checks_df, incidents_df, alerts_df, latest_df = load_dashboard_data()

    # Sidebar Controls
    with st.sidebar:
        st.header("⚙️ Monitor Controls")
        if st.button("🔄 Trigger Immediate Live Sweep", type="primary", use_container_width=True):
            with st.spinner("Probing all registered endpoints..."):
                conn = get_db_connection()
                endpoints = load_endpoints()
                for ep in endpoints:
                    if ep.get("is_active", True):
                        res = probe_endpoint(ep)
                        record_check_result(conn, res)
                conn.close()
            st.success("Live probe pass completed!")
            st.rerun()

        st.divider()
        st.subheader("📊 SLA Window")
        sla_hours = st.selectbox("Historical Window", [24, 72, 168, 720], index=0, format_func=lambda h: f"Last {h} Hours ({h//24} Days)" if h >= 24 else f"Last {h} Hours")

        conn = get_db_connection()
        sla_stats = calculate_sla(conn, hours=sla_hours)
        conn.close()

        st.metric("SLA Availability", f"{sla_stats['uptime_percent']}%")
        st.metric("Fleet Average Latency", f"{sla_stats['avg_latency_ms']} ms")
        st.metric("Total Health Checks", sla_stats["total_checks"])

        st.divider()
        st.markdown("**Author:** Rithikesh S  \n[@rithikesh18-rk](https://github.com/rithikesh18-rk)")

    # Top KPI Metrics Bar
    total_endpoints = len(latest_df)
    operational_count = len(latest_df[latest_df["status"] == "OPERATIONAL"])
    degraded_count = len(latest_df[latest_df["status"] == "DEGRADED"])
    down_count = len(latest_df[latest_df["status"] == "DOWN"])
    active_incidents = len(incidents_df[incidents_df["status"] == "OPEN"])

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Monitored Services", total_endpoints)
    with k2:
        st.metric("Operational (🟢)", operational_count)
    with k3:
        st.metric("Degraded (🟡)", degraded_count)
    with k4:
        st.metric("Outages (🔴)", down_count)
    with k5:
        st.metric("Active Incidents", active_incidents, delta=-active_incidents if active_incidents > 0 else 0, delta_color="inverse")

    st.divider()

    # Active Incidents Warning Banner
    if active_incidents > 0:
        open_inc = incidents_df[incidents_df["status"] == "OPEN"]
        for _, inc in open_inc.iterrows():
            st.error(f"🚨 **ACTIVE OUTAGE INCIDENT:** `{inc['endpoint_name']}` went DOWN at `{inc['started_at']}`. Root Cause: *{inc['root_cause']}*")

    # Main Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Live Status & Fleet Health",
        "📈 Latency Curves & Benchmarks",
        "🔒 SSL/TLS Certificate Tracker",
        "🚨 Incident History & Outages",
        "🔔 Alert Dispatch Audit",
    ])

    with tab1:
        st.subheader("Live Service Endpoints Status")

        display_df = latest_df[[
            "endpoint_name", "url", "status", "status_code",
            "response_time_ms", "ssl_days_left", "ssl_issuer", "timestamp"
        ]].copy()

        display_df.columns = [
            "Service Name", "Endpoint URL", "Status", "HTTP Code",
            "Latency (ms)", "SSL Days Remaining", "SSL Issuer", "Last Probed (UTC)"
        ]

        def highlight_status(val):
            if val == "OPERATIONAL":
                return "background-color: rgba(46, 160, 67, 0.2); color: #3fb950; font-weight: bold;"
            elif val == "DEGRADED":
                return "background-color: rgba(210, 153, 34, 0.2); color: #d29922; font-weight: bold;"
            else:
                return "background-color: rgba(248, 81, 73, 0.2); color: #f85149; font-weight: bold;"

        st.dataframe(
            display_df.style.map(highlight_status, subset=["Status"]),
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        st.subheader("Endpoint Latency Curves (Response Time ms)")
        if not checks_df.empty:
            recent_checks = checks_df.head(250).copy()
            recent_checks["timestamp"] = pd.to_datetime(recent_checks["timestamp"])

            fig = px.line(
                recent_checks.sort_values("timestamp"),
                x="timestamp",
                y="response_time_ms",
                color="endpoint_name",
                markers=True,
                title="Response Time Timeline (ms)",
                labels={"timestamp": "Probe Timestamp (UTC)", "response_time_ms": "Latency (ms)", "endpoint_name": "Endpoint"},
                template="plotly_dark",
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            # Latency statistics table
            st.markdown("#### Endpoint Latency Quantiles")
            stat_df = checks_df.groupby("endpoint_name")["response_time_ms"].agg(
                Min="min",
                Avg="mean",
                Max="max",
                StdDev="std"
            ).reset_index().round(2)
            st.dataframe(stat_df, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("SSL/TLS Certificate Validity & Expiration Watchdog")
        ssl_table = latest_df[[
            "endpoint_name", "url", "ssl_valid", "ssl_days_left", "ssl_issuer"
        ]].copy()
        ssl_table["SSL State"] = ssl_table["ssl_days_left"].apply(
            lambda d: "🟢 Healthy (>30d)" if d > 30 else ("🟡 Expiring Soon (<30d)" if d > 0 else "🔴 Expired / Invalid")
        )
        ssl_table.columns = ["Service Name", "URL", "TLS Valid", "Days Remaining", "Issuer", "Health Status"]
        st.dataframe(ssl_table, use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("Incident Timeline & Downtime Event Log")
        if incidents_df.empty:
            st.info("No recorded incidents. All services are operating cleanly within SLA.")
        else:
            inc_display = incidents_df.copy()
            inc_display.columns = ["Incident ID", "Service Name", "Started (UTC)", "Resolved (UTC)", "Downtime (s)", "Status", "Root Cause"]
            st.dataframe(inc_display, use_container_width=True, hide_index=True)

    with tab5:
        st.subheader("Outage Alerts & Notification Webhook Log")
        if alerts_df.empty:
            st.info("No alerts generated yet.")
        else:
            al_display = alerts_df.copy()
            al_display.columns = ["Alert ID", "Endpoint ID", "Timestamp (UTC)", "Alert Type", "Notification Channel", "Payload / Message", "Dispatch Status"]
            st.dataframe(al_display, use_container_width=True, hide_index=True)


def render_cli_mode():
    """Fallback CLI mode when run directly via python app.py."""
    print("=" * 82)
    print("  CLOUD WEBSITE UPTIME & ENDPOINT RELIABILITY MONITOR - CLI AUDITOR")
    print("=" * 82)
    run_single_sweep()
    print("\n[TIP] To launch the interactive visual dashboard, run:")
    print("      streamlit run app.py\n")


def main():
    if is_running_streamlit():
        render_streamlit_dashboard()
    else:
        render_cli_mode()


if __name__ == "__main__":
    main()
