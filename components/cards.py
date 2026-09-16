import streamlit as st

def render_metric_card(label: str, value: str, subtitle: str = "", border_accent: str = "#10b981", icon: str = ""):
    st.markdown(f"""
    <div class="metric-card" style="border-top: 3px solid {border_accent};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="metric-label">{label}</span>
            <span style="font-size: 1.3rem;">{icon}</span>
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def render_urgent_alert_banner(count: int, message: str):
    if count > 0:
        st.markdown(f"""
        <div class="urgent-banner">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; color: #fca5a5; font-weight: 700;">🚨 URGENT — USE FIRST ({count} Batches Requiring Action)</h4>
                    <p style="margin: 4px 0 0 0; font-size: 0.9rem; color: #cbd5e1;">{message}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
