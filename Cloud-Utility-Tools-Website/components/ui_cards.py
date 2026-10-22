"""
Reusable UI cards and rendering helpers for Cloud Utility Tools dashboard.
"""

def render_metric_badge(label: str, value: str, badge_type: str = "success") -> str:
    """Format an HTML metric card for Streamlit dashboards."""
    return f"""
    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
        <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500; text-transform: uppercase;">{label}</div>
        <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">{value}</div>
    </div>
    """

def render_status_pill(status: str, is_active: bool = True) -> str:
    """Return colored status pill."""
    bg = "rgba(16, 185, 129, 0.2)" if is_active else "rgba(239, 68, 68, 0.2)"
    color = "#34d399" if is_active else "#f87171"
    border = "rgba(16, 185, 129, 0.4)" if is_active else "rgba(239, 68, 68, 0.4)"
    return f'<span style="background: {bg}; color: {color}; border: 1px solid {border}; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem;">{status}</span>'
