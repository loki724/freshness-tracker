import streamlit as st
import os

# Set Streamlit page config as the very first Streamlit call
st.set_page_config(
    page_title="NourishAI — Smart Vegetable Freshness & Food Waste Management",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.custom_css import apply_custom_css
from components.sidebar import render_sidebar
from auth.authentication import is_logged_in
from database.seed import seed_database
from pages_ui.landing import render_landing_page
from pages_ui.dashboard import render_dashboard
from pages_ui.scanner import render_scanner
from pages_ui.donations import render_donations
from pages_ui.inventory import render_inventory
from pages_ui.alerts import render_alerts
from pages_ui.usage import render_usage
from pages_ui.waste import render_waste
from pages_ui.reports import render_reports
from pages_ui.scan_history import render_scan_history
from pages_ui.settings import render_settings
from pages_ui.profile import render_profile

# Initialize and seed database if not already initialized
seed_database()

# Apply modern dark/emerald stylesheet
apply_custom_css()

# Authentication Guard
if not is_logged_in():
    render_landing_page()
else:
    render_sidebar()
    current_page = st.session_state.get("current_page", "Dashboard")

    if current_page == "Dashboard":
        render_dashboard()
    elif current_page == "AI Scanner":
        render_scanner()
    elif current_page == "Donations":
        render_donations()
    elif current_page == "Inventory":
        render_inventory()
    elif current_page == "Alerts":
        render_alerts()
    elif current_page == "Usage":
        render_usage()
    elif current_page == "Waste":
        render_waste()
    elif current_page == "Reports":
        render_reports()
    elif current_page == "Scan History":
        render_scan_history()
    elif current_page == "Settings":
        render_settings()
    elif current_page == "Profile":
        render_profile()
    else:
        render_dashboard()
