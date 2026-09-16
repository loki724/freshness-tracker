import streamlit as st
import datetime
from database.database import SessionLocal
from database.models import Vegetable, Donation
from services.donation_service import DonationService
from services.freshness_service import FreshnessService
from services.report_service import ReportService
from auth.authentication import get_current_user

def render_donations():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            🥕 Vegetable Donations Management
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Record citizen donations, calculate Estimated Use-By Dates, and review donation logs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ Add New Donation", "📜 Donation History Log"])

    with tab1:
        st.markdown("### Manual Donation Entry")
        db = SessionLocal()
        try:
            vegetables = db.query(Vegetable).filter(Vegetable.is_active == True).all()
            veg_names = [v.name for v in vegetables]
        finally:
            db.close()

        with st.form("manual_donation_form"):
            col1, col2 = st.columns(2)
            with col1:
                donor_name = st.text_input("Donor / Organization Name", placeholder="e.g. Ramesh Kumar or Citizen Group")
                veg_name = st.selectbox("Vegetable", veg_names if veg_names else ["Tomato", "Spinach", "Carrot", "Potato", "Onion"])
                quantity = st.number_input("Quantity", min_value=0.1, value=10.0, step=0.5)
                unit = st.selectbox("Unit", ["kg", "g", "bunches", "pieces"])
            with col2:
                donation_date = st.date_input("Received Date", value=datetime.date.today())
                freshness = st.selectbox("Freshness Condition", ["FRESH", "MEDIUM", "SPOILED"], index=0)
                storage = st.selectbox("Storage Condition", ["Room Temperature", "Refrigerated", "Cool & Dark"])
                notes = st.text_area("Notes", placeholder="Optional details (e.g. farm-fresh, slightly ripe, crate #3)")

            # Interactive preview calculation
            est_use_by = FreshnessService.calculate_use_by_date(veg_name, donation_date, freshness, storage)
            days_rem = (est_use_by - datetime.date.today()).days
            st.info(f"📅 **Estimated Use-By Date**: `{est_use_by}` ({days_rem} days from today based on '{freshness}' condition and '{storage}' storage).")

            submit = st.form_submit_button("Record Donation & Add to Live Inventory", use_container_width=True)
            if submit:
                user = get_current_user()
                user_id = user["id"] if user else None
                ok, msg, don = DonationService.add_donation(
                    donor_name=donor_name,
                    vegetable_name_or_id=veg_name,
                    quantity=quantity,
                    unit=unit,
                    freshness_status=freshness,
                    storage_condition=storage,
                    donation_date=donation_date,
                    notes=notes,
                    user_id=user_id
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab2:
        st.markdown("### 📋 Complete Donation Registry")
        df = ReportService.get_donations_dataframe()
        if not df.empty:
            search = st.text_input("🔍 Search donations by donor or vegetable:", "")
            if search:
                df = df[df["Donor Name"].str.contains(search, case=False) | df["Vegetable"].str.contains(search, case=False)]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No donations recorded yet.")
