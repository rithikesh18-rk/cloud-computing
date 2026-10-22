# -*- coding: utf-8 -*-
"""
Cloud Cost Optimization & Resource Governor Dashboard
Interactive multi-cloud observability, utilization tracking, billing anomaly detection, and rightsizing engine.

Usage:
  - Run as interactive dashboard: streamlit run app.py
  - Run as CLI auditor:           python app.py
"""

import sys
import os

try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

from governor import ResourceGovernor, CloudInstance, BillingMetric


def run_cli_audit():
    """Run an automated CLI cost audit report for terminal users."""
    print("=" * 80)
    print(" [CLOUD COST OPTIMIZATION & RESOURCE GOVERNOR] TERMINAL AUDIT REPORT")
    print("=" * 80)

    governor = ResourceGovernor()
    kpis = governor.get_summary_kpis()

    print(f"\n[*] EXECUTIVE FINANCIAL SUMMARY:")
    print(f"  - Current Monthly Cloud Spend:  ${kpis['total_monthly_spend']:,.2f}")
    print(f"  - Potential Monthly Savings:   ${kpis['total_monthly_savings']:,.2f} ({kpis['waste_percentage']}% waste)")
    print(f"  - Projected Annualized ROI:     ${kpis['annualized_savings']:,.2f} / year")
    print(f"  - Post-Optimization Spend:      ${kpis['optimized_monthly_spend']:,.2f}")
    print(f"  - Fleet Inventory:              {kpis['total_instances']} instances ({kpis['idle_instances']} IDLE, {kpis['overprovisioned_instances']} OVERPROVISIONED)")

    print(f"\n[*] DETECTED IDLE INSTANCES & SHUTDOWN TARGETS:")
    print("-" * 80)
    print(f"{'ID':<16} {'NAME':<28} {'PROV':<6} {'TYPE':<16} {'CPU%':<6} {'COST/MO':<9} {'ACTION'}")
    print("-" * 80)
    for inst in governor.instances:
        if inst.governance_action == "TAG_AND_SHUTDOWN":
            print(f"{inst.instance_id:<16} {inst.name:<28} {inst.provider:<6} {inst.instance_type:<16} {inst.avg_cpu_percent:<6.1f} ${inst.current_monthly_cost:<8.2f} SHUTDOWN")

    print(f"\n[*] RIGHTSIZING DOWNGRADE RECOMMENDATIONS:")
    print("-" * 80)
    print(f"{'ID':<16} {'NAME':<24} {'CURRENT':<14} {'RECOMMENDED':<14} {'SAVINGS/MO':<12}")
    print("-" * 80)
    for inst in governor.instances:
        if inst.governance_action == "RIGHTSIZE_DOWNGRADE":
            print(f"{inst.instance_id:<16} {inst.name:<24} {inst.instance_type:<14} {inst.recommended_type:<14} ${inst.monthly_savings:<11.2f}")

    print(f"\n[*] BILLING SPIKE ANOMALIES DETECTED:")
    print("-" * 80)
    print(f"{'DATE':<12} {'PROVIDER':<8} {'SERVICE':<18} {'COST':<10} {'SCORE':<7} {'ROOT CAUSE'}")
    print("-" * 80)
    anomalies = governor.detect_billing_anomalies()
    for anom in anomalies:
        print(f"{anom.date:<12} {anom.provider:<8} {anom.service:<18} ${anom.cost_usd:<9.2f} {anom.anomaly_score:<6.1f}s {anom.root_cause}")

    print("\n" + "=" * 80)
    print(" To explore the interactive visual analytics dashboard, run:")
    print("    streamlit run app.py")
    print("=" * 80 + "\n")


def run_streamlit_dashboard():
    """Render the full interactive Streamlit UI."""
    st.set_page_config(
        page_title="Cloud Cost Optimization & Resource Governor",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    governor = ResourceGovernor()
    kpis = governor.get_summary_kpis()

    # Custom Header Styling
    st.markdown(
        """
        <style>
        .metric-card {
            background-color: #1E293B;
            border-radius: 10px;
            padding: 16px;
            border-left: 5px solid #3B82F6;
            margin-bottom: 12px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #F8FAFC;
        }
        .metric-label {
            font-size: 13px;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Title & Subheading
    st.title("💰 Cloud Cost Optimization & Resource Governor")
    st.caption("Automated multi-cloud resource monitoring, idle-instance detection, rightsizing recommendations, and billing anomaly detection.")

    # Sidebar Filter Controls
    st.sidebar.image("https://img.icons8.com/color/96/cloud-lighting.png", width=64)
    st.sidebar.title("Governor Controls")
    
    selected_providers = st.sidebar.multiselect(
        "Cloud Providers",
        options=["AWS", "GCP", "Azure"],
        default=["AWS", "GCP", "Azure"],
    )

    min_cpu_threshold = st.sidebar.slider(
        "Idle CPU Threshold (%)",
        min_value=1.0,
        max_value=15.0,
        value=5.0,
        step=0.5,
        help="Instances with average CPU below this threshold are flagged as IDLE.",
    )

    savings_target_pct = st.sidebar.slider(
        "Target Optimization Scope (%)",
        min_value=20,
        max_value=100,
        value=100,
        step=5,
        help="Simulate phased roll-out of recommendations.",
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Stack:** Python 3.11, Streamlit, Plotly, Multi-Cloud APIs\n\n"
        "**Status:** 🟢 Connected to AWS, GCP, and Azure Telemetry Feeds"
    )

    # KPI Top Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Monthly Spend",
            value=f"${kpis['total_monthly_spend']:,.2f}",
            delta="-Baseline",
            delta_color="off",
        )
    with col2:
        applied_savings = kpis['total_monthly_savings'] * (savings_target_pct / 100.0)
        st.metric(
            label="Identifiable Waste / Mo",
            value=f"${applied_savings:,.2f}",
            delta=f"-{kpis['waste_percentage']}% of OpEx",
            delta_color="inverse",
        )
    with col3:
        st.metric(
            label="Annualized Projected ROI",
            value=f"${applied_savings * 12:,.2f}",
            delta="Recurring Savings",
            delta_color="normal",
        )
    with col4:
        st.metric(
            label="Actionable Targets",
            value=f"{kpis['idle_instances']} Idle / {kpis['overprovisioned_instances']} Rightsize",
            delta=f"{kpis['total_instances']} Total Instances",
            delta_color="off",
        )

    st.markdown("---")

    # Main Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Fleet Utilization & Metrics",
        "🎯 Rightsizing & Idle Governor",
        "🚨 Billing Anomaly Detection",
        "📈 Spend Allocation & Forecast",
    ])

    # Convert instances to DataFrame
    inst_records = []
    for inst in governor.instances:
        if inst.provider in selected_providers:
            inst_records.append({
                "Instance ID": inst.instance_id,
                "Name": inst.name,
                "Provider": inst.provider,
                "Region": inst.region,
                "Environment": inst.tags.get("Env", "Unknown"),
                "Type": inst.instance_type,
                "vCPU": inst.vcpu,
                "RAM (GB)": inst.ram_gb,
                "Monthly Cost ($)": inst.current_monthly_cost,
                "Avg CPU (%)": inst.avg_cpu_percent,
                "Max CPU (%)": inst.max_cpu_percent,
                "Avg RAM (%)": inst.avg_memory_percent,
                "Disk IOPS": inst.avg_disk_iops,
                "State": inst.state,
                "Days Idle": inst.days_idle,
                "Recommended Type": inst.recommended_type,
                "Monthly Savings ($)": inst.monthly_savings,
                "Governor Action": inst.governance_action,
                "Reason": inst.recommendation_reason,
            })
    df_inst = pd.DataFrame(inst_records)

    # TAB 1: FLEET UTILIZATION
    with tab1:
        st.subheader("🖥️ Cloud Infrastructure Utilization Telemetry")
        st.caption("Live monitoring of compute utilization, memory pressure, and I/O profiles across cloud fleets.")

        if not df_inst.empty:
            c1, c2 = st.columns([3, 2])
            with c1:
                fig_scatter = px.scatter(
                    df_inst,
                    x="Avg CPU (%)",
                    y="Avg RAM (%)",
                    size="Monthly Cost ($)",
                    color="State",
                    hover_name="Name",
                    hover_data=["Provider", "Type", "Monthly Cost ($)"],
                    color_discrete_map={"RUNNING": "#10B981", "IDLE": "#EF4444", "STOPPED": "#6B7280"},
                    title="Resource Utilization Matrix (CPU % vs. Memory % vs. Spend Size)",
                )
                fig_scatter.add_vline(x=15, line_dash="dash", line_color="orange", annotation_text="Underutilized Bound")
                fig_scatter.add_hline(y=30, line_dash="dash", line_color="orange")
                st.plotly_chart(fig_scatter, use_container_width=True)

            with c2:
                fig_hist = px.bar(
                    df_inst.groupby("Provider")["Monthly Cost ($)"].sum().reset_index(),
                    x="Provider",
                    y="Monthly Cost ($)",
                    color="Provider",
                    title="Current Monthly Spend by Cloud Provider",
                    color_discrete_map={"AWS": "#FF9900", "GCP": "#4285F4", "Azure": "#0089D6"},
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            st.dataframe(
                df_inst[["Instance ID", "Name", "Provider", "Region", "Environment", "Type", "Avg CPU (%)", "Avg RAM (%)", "Disk IOPS", "Monthly Cost ($)", "State"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("No instances match current filter criteria.")

    # TAB 2: RIGHTSIZING & IDLE GOVERNOR
    with tab2:
        st.subheader("🎯 Automated Rightsizing Recommendations & Idle Shutdown Policies")
        st.caption("Identifies over-provisioned compute blocks and enforces automated cost reduction governance.")

        action_filter = st.radio(
            "Filter Recommendations:",
            options=["All Targets", "Idle Shutdown Only", "Rightsizing Downsizes Only"],
            horizontal=True,
        )

        filtered_df = df_inst.copy()
        if action_filter == "Idle Shutdown Only":
            filtered_df = filtered_df[filtered_df["Governor Action"] == "TAG_AND_SHUTDOWN"]
        elif action_filter == "Rightsizing Downsizes Only":
            filtered_df = filtered_df[filtered_df["Governor Action"] == "RIGHTSIZE_DOWNGRADE"]
        else:
            filtered_df = filtered_df[filtered_df["Governor Action"] != "MAINTAIN"]

        if not filtered_df.empty:
            for idx, row in filtered_df.iterrows():
                with st.expander(f"{'🛑' if row['Governor Action'] == 'TAG_AND_SHUTDOWN' else '⚡'} {row['Name']} ({row['Provider']} - {row['Instance ID']}) — Save ${row['Monthly Savings ($)']:.2f}/mo"):
                    c_a, c_b, c_c = st.columns([2, 2, 1])
                    with c_a:
                        st.markdown(f"**Current Configuration:** `{row['Type']}` ({row['vCPU']} vCPU, {row['RAM (GB)']} GB RAM)")
                        st.markdown(f"**Utilization Profile:** Avg CPU: **{row['Avg CPU (%)']}%** | Max CPU: **{row['Max CPU (%)']}%** | RAM: **{row['Avg RAM (%)']}%**")
                    with c_b:
                        st.markdown(f"**Recommendation:** `{row['Recommended Type']}`")
                        st.markdown(f"**Policy Rationale:** {row['Reason']}")
                    with c_c:
                        st.success(f"**Monthly Savings:**\n### ${row['Monthly Savings ($)']:.2f}")
                        if st.button(f"Apply Policy", key=f"btn_{row['Instance ID']}"):
                            st.toast(f"Governance Action scheduled for {row['Name']}: {row['Governor Action']}", icon="✅")
        else:
            st.info("No actionable targets found matching this filter.")

    # TAB 3: ANOMALY DETECTION
    with tab3:
        st.subheader("🚨 Multi-Cloud Billing Metric Anomaly Detection")
        st.caption("Continuous statistical tracking of daily line-item disbursements to prevent runaway infrastructure billing.")

        # Billing history data
        billing_records = [
            {
                "Date": b.date,
                "Provider": b.provider,
                "Service": b.service,
                "Cost ($)": b.cost_usd,
                "Is Anomaly": b.is_anomaly,
                "Expected Cost ($)": b.expected_cost,
                "Anomaly Score": b.anomaly_score,
                "Root Cause": b.root_cause,
            }
            for b in governor.billing_history
            if b.provider in selected_providers
        ]
        df_bill = pd.DataFrame(billing_records)

        if not df_bill.empty:
            # Aggregate daily spend
            daily_total = df_bill.groupby("Date")["Cost ($)"].sum().reset_index()
            daily_total["3-Day Rolling Avg"] = daily_total["Cost ($)"].rolling(window=3, min_periods=1).mean()

            fig_anomaly = go.Figure()
            fig_anomaly.add_trace(go.Scatter(x=daily_total["Date"], y=daily_total["Cost ($)"], mode="lines+markers", name="Actual Daily Spend ($)", line=dict(color="#3B82F6", width=2)))
            fig_anomaly.add_trace(go.Scatter(x=daily_total["Date"], y=daily_total["3-Day Rolling Avg"], mode="lines", name="Expected Rolling Baseline", line=dict(color="#94A3B8", dash="dot")))

            # Highlight anomalies
            anom_points = df_bill[df_bill["Is Anomaly"]]
            if not anom_points.empty:
                fig_anomaly.add_trace(go.Scatter(
                    x=anom_points["Date"],
                    y=anom_points["Cost ($)"],
                    mode="markers",
                    marker=dict(color="#EF4444", size=14, symbol="cross"),
                    name="Billing Anomaly Detected",
                    text=anom_points["Root Cause"],
                ))

            fig_anomaly.update_layout(title="30-Day Multi-Cloud Spending Trend with Anomaly Deviations", xaxis_title="Date", yaxis_title="Daily Spend (USD)")
            st.plotly_chart(fig_anomaly, use_container_width=True)

            st.markdown("#### 🚩 Incident Log & Anomaly Explanations")
            st.dataframe(
                anom_points[["Date", "Provider", "Service", "Cost ($)", "Expected Cost ($)", "Anomaly Score", "Root Cause"]],
                use_container_width=True,
                hide_index=True,
            )

    # TAB 4: SPEND ALLOCATION & SAVINGS PROJECTION
    with tab4:
        st.subheader("📈 Multi-Cloud Cost Allocation & 12-Month Projected Savings")

        col_x, col_y = st.columns(2)
        with col_x:
            fig_pie = px.pie(
                df_inst,
                names="Environment",
                values="Monthly Cost ($)",
                title="Spend Allocation by Environment Tier",
                color_discrete_sequence=px.colors.sequential.Teal,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_y:
            # 12-Month Projections
            months = [f"Month {m}" for m in range(1, 13)]
            baseline_proj = [kpis['total_monthly_spend'] * (1 + 0.02 * m) for m in range(12)]
            optimized_proj = [kpis['total_monthly_spend'] * (1 + 0.02 * m) - (applied_savings * min(1.0, 0.4 + 0.05 * m)) for m in range(12)]

            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(x=months, y=baseline_proj, mode="lines+markers", name="Unmanaged Baseline OpEx", line=dict(color="#EF4444", width=2)))
            fig_proj.add_trace(go.Scatter(x=months, y=optimized_proj, mode="lines+markers", name="With Governor Optimization", line=dict(color="#10B981", width=2)))
            fig_proj.update_layout(title="12-Month Cumulative OpEx Projection ($ USD)", yaxis_title="Projected Monthly Spend")
            st.plotly_chart(fig_proj, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #64748B; font-size: 13px;'>"
        "Cloud Cost Optimization & Resource Governor Hub • Multi-Cloud CloudOps Architecture"
        "</div>",
        unsafe_allow_html=True,
    )


def is_running_under_streamlit() -> bool:
    """Check if app is being executed via `streamlit run`."""
    if not HAS_STREAMLIT:
        return False
    try:
        from streamlit.runtime.scriptrunner import get_script_run_context
        return get_script_run_context() is not None
    except Exception:
        return False


if __name__ == "__main__":
    if is_running_under_streamlit():
        run_streamlit_dashboard()
    else:
        run_cli_audit()
