import streamlit as st
import datetime
from sqlalchemy.orm import joinedload
from database.database import SessionLocal
from database.models import Inventory
from services.waste_service import WasteService
from services.report_service import ReportService
from auth.authentication import get_current_user

def render_usage():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            🍲 Food Usage Tracking
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Record vegetables used in meal preparations. Inventory stock levels will automatically decrement.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📝 Record Meal Usage", "📋 Usage History Log"])

    with tab1:
        db = SessionLocal()
        try:
            active_items = (
                db.query(Inventory)
                .options(joinedload(Inventory.vegetable))
                .filter(Inventory.status == "In Stock", Inventory.current_quantity > 0)
                .all()
            )
            item_options = {
                f"INV-{i.id:04d} | {i.vegetable.name} (Stock: {i.current_quantity} {i.unit}) - Use by {i.estimated_use_by_date}": i.id
                for i in active_items
            }
        finally:
            db.close()

        if not item_options:
            st.warning("No available vegetable stock in inventory to record usage from.")
        else:
            with st.form("record_usage_form"):
                user = get_current_user()
                selected_label = st.selectbox("Select Vegetable Stock Batch", list(item_options.keys()))
                inv_id = item_options[selected_label]
                
                col1, col2 = st.columns(2)
                with col1:
                    qty = st.number_input("Quantity Used", min_value=0.1, value=2.0, step=0.5)
                    meal = st.selectbox("Meal / Purpose", ["Lunch for Children", "Dinner for Community", "Breakfast Soup", "Curry Preparation", "Other"])
                with col2:
                    date_used = st.date_input("Date Used", value=datetime.date.today())
                    staff_name = st.text_input("Kitchen Staff Name", value=user.get("full_name", "Kitchen Staff") if user else "Kitchen Staff")
                
                notes = st.text_input("Notes", placeholder="Optional recipe / kitchen details")
                submit = st.form_submit_button("Record Usage & Deduct Inventory", use_container_width=True)

                if submit:
                    ok, msg = WasteService.record_usage(
                        inventory_id=inv_id,
                        quantity_used=qty,
                        staff_name=staff_name,
                        meal_purpose=meal,
                        date_used=date_used,
                        notes=notes
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab2:
        st.markdown("### 📋 Historical Food Usage Logs")
        df = ReportService.get_usage_dataframe()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No usage logged yet.")
