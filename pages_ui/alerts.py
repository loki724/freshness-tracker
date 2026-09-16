import streamlit as st
from services.alert_service import AlertService


ALERT_STYLE = {
    "SPOILED": {
        "icon": "🔴",
        "border": "#ef4444",
        "bg": "rgba(239, 68, 68, 0.15)",
        "label": "SPOILED — Do Not Use",
    },
    "URGENT": {
        "icon": "🟠",
        "border": "#f97316",
        "bg": "rgba(249, 115, 22, 0.15)",
        "label": "URGENT — Use Within 24 Hours",
    },
    "USE_SOON": {
        "icon": "🟡",
        "border": "#eab308",
        "bg": "rgba(234, 179, 8, 0.15)",
        "label": "USE SOON — Medium Freshness",
    },
    # legacy fallback names
    "EXPIRED": {
        "icon": "🔴",
        "border": "#ef4444",
        "bg": "rgba(239, 68, 68, 0.15)",
        "label": "EXPIRED — Do Not Use",
    },
    "EXPIRING_SOON": {
        "icon": "🟠",
        "border": "#f97316",
        "bg": "rgba(249, 115, 22, 0.15)",
        "label": "EXPIRING SOON",
    },
}

DEFAULT_STYLE = {
    "icon": "⚠️",
    "border": "#94a3b8",
    "bg": "rgba(148, 163, 184, 0.15)",
    "label": "ALERT",
}


def render_alerts():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            ⚠️ Freshness &amp; Shelf-Life Alerts
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Automated alerts for vegetable batches that are spoiled, expiring within 24 hours, or approaching their use-by limit.
        </p>
    </div>
    """, unsafe_allow_html=True)

    alerts = AlertService.get_active_alerts()

    if not alerts:
        st.success(
            "🎉 All clear! No urgent freshness alerts. Every vegetable batch is well within its safe shelf-life.",
            icon="✅"
        )
    else:
        # Summary badges
        counts = {"SPOILED": 0, "URGENT": 0, "USE_SOON": 0}
        for a in alerts:
            key = str(a.alert_type).upper()
            if "SPOIL" in key or "EXPIR" in key and "SOON" not in key:
                counts["SPOILED"] += 1
            elif "URGENT" in key or ("EXPIR" in key and "SOON" in key):
                counts["URGENT"] += 1
            else:
                counts["USE_SOON"] += 1

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""
            <div style="background: rgba(239,68,68,0.15); border-radius: 10px; padding: 12px; text-align:center;">
                <div style="font-size:1.8rem;">🔴</div>
                <div style="font-size:1.4rem; font-weight:800; color:#ef4444;">{counts['SPOILED']}</div>
                <div style="font-size:0.8rem; color:#94a3b8; text-transform:uppercase;">Spoiled</div>
            </div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div style="background: rgba(249,115,22,0.15); border-radius: 10px; padding: 12px; text-align:center;">
                <div style="font-size:1.8rem;">🟠</div>
                <div style="font-size:1.4rem; font-weight:800; color:#f97316;">{counts['URGENT']}</div>
                <div style="font-size:0.8rem; color:#94a3b8; text-transform:uppercase;">Urgent</div>
            </div>""", unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""
            <div style="background: rgba(234,179,8,0.15); border-radius: 10px; padding: 12px; text-align:center;">
                <div style="font-size:1.8rem;">🟡</div>
                <div style="font-size:1.4rem; font-weight:800; color:#eab308;">{counts['USE_SOON']}</div>
                <div style="font-size:0.8rem; color:#94a3b8; text-transform:uppercase;">Use Soon</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"### Active Alerts ({len(alerts)})")
        st.markdown("")

        for alert in alerts:
            alert_key = str(alert.alert_type).upper()
            style = ALERT_STYLE.get(alert_key, DEFAULT_STYLE)
            icon = style["icon"]
            border_color = style["border"]
            bg_color = style["bg"]
            label = style["label"]

            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div style="background: {bg_color}; border-left: 5px solid {border_color}; border-radius: 8px; padding: 14px; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.3rem;">{icon}</span>
                        <strong style="font-size: 1rem; color: #f8fafc;">{label}</strong>
                    </div>
                    <p style="margin: 6px 0 0 0; color: #e2e8f0; font-size: 0.95rem;">{alert.message}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✅ Resolve", key=f"res_alert_{alert.id}", use_container_width=True):
                    AlertService.resolve_alert(alert.id)
                    st.success("Alert resolved!")
                    st.rerun()
