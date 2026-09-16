import streamlit as st
from auth.authentication import get_current_user, logout_user
from ai.model_manager import ModelManager

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 12px 0 16px 0;">
            <div style="font-size: 2.2rem; margin-bottom: 2px;">🌱</div>
            <h2 style="margin: 0; color: #10b981; font-weight: 800; font-size: 1.4rem;">NourishAI</h2>
            <p style="margin: 0; font-size: 0.75rem; color: #94a3b8; letter-spacing: 0.05em;">SMART VEGETABLE TRACKER</p>
        </div>
        """, unsafe_allow_html=True)

        user = get_current_user()
        if user:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 10px 14px; margin-bottom: 16px;">
                <div style="font-size: 0.8rem; color: #94a3b8;">Logged in as:</div>
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{user.get('full_name')}</div>
                <div style="font-size: 0.75rem; color: #10b981; font-weight: 600;">🏷️ {user.get('role')}</div>
            </div>
            """, unsafe_allow_html=True)

        menu_items = [
            ("🏠 Dashboard", "Dashboard"),
            ("📷 AI Scanner", "AI Scanner"),
            ("🥕 Donations", "Donations"),
            ("📦 Inventory", "Inventory"),
            ("⚠️ Alerts", "Alerts"),
            ("🍲 Usage", "Usage"),
            ("🗑️ Waste", "Waste"),
            ("📊 Reports", "Reports"),
            ("📜 Scan History", "Scan History"),
            ("⚙️ Settings", "Settings"),
            ("👤 Profile", "Profile")
        ]

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"

        st.markdown("### Navigation")
        for label, page_name in menu_items:
            is_active = (st.session_state.current_page == page_name)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{page_name}", use_container_width=True, type=btn_type):
                st.session_state.current_page = page_name
                st.rerun()

        st.markdown("---")
        status = ModelManager.get_model_status()
        if status["custom_model_available"]:
            st.success("🤖 Custom YOLOv8 Loaded", icon="✅")
        else:
            st.info("💡 AI Simulation Mode Active", icon="ℹ️")

        if user:
            if st.button("🚪 Logout", key="sidebar_logout_btn", use_container_width=True):
                logout_user()
                st.rerun()

        st.markdown("""
        <div style="text-align: center; font-size: 0.7rem; color: #64748b; margin-top: 20px;">
            Santhi Welfare Children Home • Food Waste Reduction Initiative
        </div>
        """, unsafe_allow_html=True)
