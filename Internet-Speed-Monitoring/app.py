#!/usr/bin/env python3
"""
Real-Time Internet Speed & Network Reliability Monitor
Interactive Web Dashboard & Network Telemetry Visualizer

Usage:
  - Interactive Streamlit Dashboard: streamlit run app.py
  - CLI Network Telemetry Report:     python app.py
"""

import os
import sys
import sqlite3
from datetime import datetime, timezone

try:
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

from monitor import (
    DB_FILE,
    CSV_FILE,
    DEFAULT_SLA,
    init_db,
    run_benchmark,
    seed_historical_telemetry
)


def load_telemetry_df():
    """Loads historical network telemetry from SQLite database into pandas DataFrame."""
    init_db()
    seed_historical_telemetry()
    conn = sqlite3.connect(DB_FILE)
    query = """
        SELECT id, timestamp, ping_ms, jitter_ms, download_mbps, upload_mbps,
               packet_loss_pct, isp, server_name, status, sla_compliant, violation_reasons
        FROM network_metrics
        ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        df["datetime"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["datetime"].dt.hour
        df["date"] = df["datetime"].dt.date
    return df


def run_cli_report():
    """Runs a summary network telemetry report in the terminal."""
    print("=" * 75)
    print("  INTERNET SPEED & NETWORK RELIABILITY MONITOR - CLI AUDIT")
    print("=" * 75)
    init_db()
    seed_historical_telemetry()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*),
               AVG(download_mbps),
               AVG(upload_mbps),
               AVG(ping_ms),
               AVG(jitter_ms),
               SUM(CASE WHEN sla_compliant = 1 THEN 1 ELSE 0 END)
        FROM network_metrics
    """)
    row = cursor.fetchone()
    total_tests = row[0]
    avg_down = row[1] or 0.0
    avg_up = row[2] or 0.0
    avg_ping = row[3] or 0.0
    avg_jitter = row[4] or 0.0
    compliant_tests = row[5] or 0
    sla_pct = (compliant_tests / total_tests * 100.0) if total_tests > 0 else 0.0

    print(f"\nTotal Telemetry Benchmarks: {total_tests}")
    print(f"Overall ISP SLA Compliance:  {sla_pct:.1f}% ({compliant_tests}/{total_tests} tests)")
    print(f"Average Download Bandwidth: {avg_down:.2f} Mbps")
    print(f"Average Upload Bandwidth:   {avg_up:.2f} Mbps")
    print(f"Average Handshake Latency:  {avg_ping:.2f} ms")
    print(f"Average Network Jitter:     {avg_jitter:.2f} ms")

    cursor.execute("""
        SELECT timestamp, download_mbps, upload_mbps, ping_ms, jitter_ms, status, sla_compliant
        FROM network_metrics
        ORDER BY timestamp DESC LIMIT 5
    """)
    recent = cursor.fetchall()
    print("\nRecent 5 Network Benchmarks:")
    print("-" * 75)
    print(f"{'Timestamp':<20} {'Down (Mbps)':<12} {'Up (Mbps)':<12} {'Ping':<8} {'Jitter':<8} {'SLA':<8}")
    print("-" * 75)
    for r in recent:
        sla_tag = "PASS" if r[6] == 1 else "FAIL"
        print(f"{r[0]:<20} {r[1]:<12.2f} {r[2]:<12.2f} {r[3]:<8.2f} {r[4]:<8.2f} {sla_tag:<8}")
    print("=" * 75)
    conn.close()


def render_dashboard():
    """Renders the interactive Streamlit telemetry dashboard."""
    st.set_page_config(
        page_title="Internet Speed & Network Reliability Monitor",
        page_icon="📶",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom styling
    st.markdown("""
        <style>
        .metric-card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
        }
        .metric-title { color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
        .metric-val { color: #f8fafc; font-size: 1.8rem; font-weight: 700; }
        .metric-sub { color: #38bdf8; font-size: 0.8rem; }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar Controls
    st.sidebar.title("⚙️ Telemetry Controls")
    st.sidebar.markdown("Configure Service Level Agreement (SLA) baselines to detect ISP throttling and SLA breaches.")

    sla_down = st.sidebar.slider("Min Download SLA (Mbps)", 10, 500, int(DEFAULT_SLA["min_download_mbps"]), 10)
    sla_up = st.sidebar.slider("Min Upload SLA (Mbps)", 5, 200, int(DEFAULT_SLA["min_upload_mbps"]), 5)
    sla_ping = st.sidebar.slider("Max Latency SLA (ms)", 5, 150, int(DEFAULT_SLA["max_ping_ms"]), 5)
    sla_jitter = st.sidebar.slider("Max Jitter SLA (ms)", 1, 50, int(DEFAULT_SLA["max_jitter_ms"]), 1)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 Live Benchmark")
    if st.sidebar.button("Run Network Test Now", use_container_width=True):
        with st.sidebar.status("Running benchmark..."):
            res = run_benchmark()
        st.sidebar.success(f"Benchmark finished: {res['download_mbps']} Mbps Down / {res['upload_mbps']} Mbps Up")

    df = load_telemetry_df()

    if df.empty:
        st.warning("No telemetry records found. Run `python monitor.py --benchmark` to record telemetry.")
        return

    # Title & Overview
    st.title("📶 Real-Time Internet Speed & Network Reliability Monitor")
    st.markdown(
        "Automated network telemetry engine tracking latency, jitter, download/upload throughput, and ISP SLA compliance."
    )

    latest = df.iloc[-1]
    total_records = len(df)
    sla_compliant_count = int(df["sla_compliant"].sum())
    overall_sla_pct = (sla_compliant_count / total_records) * 100.0 if total_records > 0 else 0.0

    # Top KPI Metrics Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric(
            label="Download Speed",
            value=f"{latest['download_mbps']:.1f} Mbps",
            delta=f"{latest['download_mbps'] - sla_down:+.1f} vs SLA"
        )
    with c2:
        st.metric(
            label="Upload Speed",
            value=f"{latest['upload_mbps']:.1f} Mbps",
            delta=f"{latest['upload_mbps'] - sla_up:+.1f} vs SLA"
        )
    with c3:
        st.metric(
            label="Handshake Latency",
            value=f"{latest['ping_ms']:.1f} ms",
            delta=f"{latest['ping_ms'] - sla_ping:+.1f} vs SLA",
            delta_color="inverse"
        )
    with c4:
        st.metric(
            label="Network Jitter",
            value=f"{latest['jitter_ms']:.1f} ms",
            delta=f"{latest['jitter_ms'] - sla_jitter:+.1f} vs SLA",
            delta_color="inverse"
        )
    with c5:
        st.metric(
            label="Packet Loss",
            value=f"{latest['packet_loss_pct']:.1f}%",
            delta="Normal" if latest['packet_loss_pct'] == 0 else "Drops Detected",
            delta_color="inverse"
        )
    with c6:
        st.metric(
            label="ISP SLA Health",
            value=f"{overall_sla_pct:.1f}%",
            delta=f"{sla_compliant_count}/{total_records} Passed"
        )

    st.markdown("---")

    # Tabs for Data Views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Bandwidth & Latency Trends",
        "🕒 Hourly ISP Throttling Analysis",
        "📊 Throughput Distribution & Jitter",
        "📋 SLA Violations & Telemetry Log"
    ])

    with tab1:
        st.subheader("Historical Bandwidth Throughput (Mbps)")
        fig_bw = go.Figure()
        fig_bw.add_trace(go.Scatter(
            x=df["datetime"], y=df["download_mbps"],
            mode="lines+markers", name="Download Mbps",
            line=dict(color="#38bdf8", width=2),
            marker=dict(size=4)
        ))
        fig_bw.add_trace(go.Scatter(
            x=df["datetime"], y=df["upload_mbps"],
            mode="lines+markers", name="Upload Mbps",
            line=dict(color="#a855f7", width=2),
            marker=dict(size=4)
        ))
        fig_bw.add_hline(
            y=sla_down, line_dash="dash", line_color="#ef4444",
            annotation_text=f"Min Download SLA ({sla_down} Mbps)"
        )
        fig_bw.add_hline(
            y=sla_up, line_dash="dash", line_color="#f59e0b",
            annotation_text=f"Min Upload SLA ({sla_up} Mbps)"
        )
        fig_bw.update_layout(
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bw, use_container_width=True)

        st.subheader("Handshake Latency & Jitter Reliability (ms)")
        fig_ping = go.Figure()
        fig_ping.add_trace(go.Scatter(
            x=df["datetime"], y=df["ping_ms"],
            mode="lines", name="Ping Latency (ms)",
            line=dict(color="#f43f5e", width=2)
        ))
        fig_ping.add_trace(go.Scatter(
            x=df["datetime"], y=df["jitter_ms"],
            mode="lines", name="Jitter (ms)",
            line=dict(color="#10b981", width=2)
        ))
        fig_ping.add_hline(
            y=sla_ping, line_dash="dash", line_color="#ef4444",
            annotation_text=f"Max Latency SLA ({sla_ping} ms)"
        )
        fig_ping.update_layout(
            template="plotly_dark",
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_ping, use_container_width=True)

    with tab2:
        st.subheader("Diurnal Throttling Pattern: Average Download by Hour of Day")
        st.markdown(
            "Identifies recurring peak-hour bandwidth throttling where the ISP fails to meet contracted SLA commitments."
        )
        hourly_summary = df.groupby("hour").agg({
            "download_mbps": ["mean", "min", "max"],
            "ping_ms": "mean",
            "sla_compliant": lambda x: (x.sum() / len(x)) * 100.0
        }).reset_index()
        hourly_summary.columns = ["hour", "avg_down", "min_down", "max_down", "avg_ping", "sla_compliance_pct"]

        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Bar(
            x=hourly_summary["hour"],
            y=hourly_summary["avg_down"],
            name="Avg Download (Mbps)",
            marker_color=["#ef4444" if d < sla_down else "#3b82f6" for d in hourly_summary["avg_down"]],
            text=[f"{v:.1f}" for v in hourly_summary["avg_down"]],
            textposition="auto"
        ))
        fig_hourly.add_hline(
            y=sla_down, line_dash="dash", line_color="#ef4444",
            annotation_text=f"SLA Target ({sla_down} Mbps)"
        )
        fig_hourly.update_layout(
            template="plotly_dark",
            xaxis=dict(title="Hour of Day (00:00 - 23:00 UTC)", tickmode="linear", dtick=1),
            yaxis=dict(title="Download Bandwidth (Mbps)"),
            height=380,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_hourly, use_container_width=True)

    with tab3:
        st.subheader("Bandwidth Distribution & Latency Spread")
        col_dist1, col_dist2 = st.columns(2)

        with col_dist1:
            fig_hist = px.histogram(
                df, x="download_mbps", nbins=30,
                title="Download Throughput Distribution",
                color_discrete_sequence=["#38bdf8"],
                template="plotly_dark"
            )
            fig_hist.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_dist2:
            fig_box = px.box(
                df, y="ping_ms", points="all",
                title="Ping Latency Variation & Outliers",
                color_discrete_sequence=["#f43f5e"],
                template="plotly_dark"
            )
            fig_box.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_box, use_container_width=True)

    with tab4:
        st.subheader("Historical SLA Violations & Network Incidents")
        violations_df = df[df["sla_compliant"] == 0].copy()

        st.markdown(f"**Total Incidents Detected:** {len(violations_df)} of {len(df)} tests")
        if not violations_df.empty:
            display_cols = ["timestamp", "download_mbps", "upload_mbps", "ping_ms", "jitter_ms", "packet_loss_pct", "status", "violation_reasons"]
            st.dataframe(
                violations_df[display_cols].sort_values(by="timestamp", ascending=False),
                use_container_width=True,
                height=320
            )
        else:
            st.success("No SLA violations detected! 100% compliant network performance.")

        st.markdown("### 📥 Export Telemetry Logs")
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Complete CSV Telemetry Log",
            data=csv_data,
            file_name="internet_speed_telemetry_export.csv",
            mime="text/csv"
        )


def is_running_streamlit():
    """Detect if running under streamlit CLI."""
    if any("streamlit" in arg.lower() for arg in sys.argv[:2]):
        return True
    if os.environ.get("STREAMLIT_SERVER_PORT") or os.environ.get("STREAMLIT_SERVER_ADDRESS"):
        return True
    return False


def main():
    if HAS_STREAMLIT and is_running_streamlit():
        render_dashboard()
    else:
        run_cli_report()


if __name__ == "__main__":
    main()
