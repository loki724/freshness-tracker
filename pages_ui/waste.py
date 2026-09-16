import streamlit as st
import datetime
from sqlalchemy.orm import joinedload
from database.database import SessionLocal
from database.models import Inventory
from services.waste_service import WasteService
from services.report_service import ReportService

def render_waste():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            🗑️ Food Waste Tracking & Analytics
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Log spoiled, damaged, or excess food waste to compute waste percentage and identify root causes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    metrics = WasteService.get_waste_metrics()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Donated", f"{metrics['total_donated_qty']} kg")
    with c2:
        st.metric("Total Used", f"{metrics['total_used_qty']} kg")
    with c3:
        st.metric("Total Wasted", f"{metrics['total_wasted_qty']} kg")
    with c4:
        st.metric("Waste Percentage", f"{metrics['waste_percentage']}%", delta=f"{metrics['waste_percentage']}%", delta_color="inverse")

    st.markdown("---")

    tab1, tab2 = st.tabs(["⚠️ Log Food Waste", "📊 Waste History & Breakdown"])

    with tab1:
        db = SessionLocal()
        try:
            active_items = (
                db.query(Inventory)
                .options(joinedload(Inventory.vegetable))
                .filter(Inventory.current_quantity > 0)
                .all()
            )
            item_options = {
                f"INV-{i.id:04d} | {i.vegetable.name} (Available: {i.current_quantity} {i.unit})": i.id
                for i in active_items
            }
        finally:
            db.close()

        if not item_options:
            st.warning("No active inventory items available to log waste against.")
        else:
            with st.form("record_waste_form"):
                selected_label = st.selectbox("Select Batch", list(item_options.keys()))
                inv_id = item_options[selected_label]
                
                col1, col2 = st.columns(2)
                with col1:
                    qty = st.number_input("Quantity Wasted (kg)", min_value=0.1, value=1.0, step=0.5)
                    reason = st.selectbox("Waste Reason", ["Spoiled", "Overripe", "Damaged", "Excess", "Other"])
                with col2:
                    date_wasted = st.date_input("Date Wasted", value=datetime.date.today())
                    notes = st.text_input("Notes", placeholder="Details on why the vegetable was discarded")

                submit = st.form_submit_button("Log Waste Record", use_container_width=True)
                if submit:
                    ok, msg = WasteService.record_waste(
                        inventory_id=inv_id,
                        quantity_wasted=qty,
                        reason=reason,
                        date_wasted=date_wasted,
                        notes=notes
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab2:
        st.markdown("### 📋 Waste Record History")
        df = ReportService.get_waste_dataframe()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No food waste recorded yet. Great work!")
