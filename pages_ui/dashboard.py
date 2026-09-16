import streamlit as st
import datetime
from sqlalchemy.orm import joinedload
from database.database import SessionLocal
from database.models import Inventory, Donation
from services.waste_service import WasteService
from services.freshness_service import FreshnessService
from services.report_service import ReportService
from components.cards import render_metric_card, render_urgent_alert_banner
from components.charts import plot_inventory_by_category, plot_freshness_distribution, plot_usage_vs_waste, plot_waste_by_reason

def render_dashboard():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            🌱 NourishAI <span style="color: #10b981; font-size: 1.3rem; font-weight: 500;">| Smart Vegetable Freshness & Waste Management</span>
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Real-time donation tracking, 3-level freshness classification (<strong>FRESH</strong>, <strong>MEDIUM</strong>, <strong>SPOILED</strong>), and priority kitchen cooking engine.
        </p>
    </div>
    """, unsafe_allow_html=True)

    metrics = WasteService.get_waste_metrics()
    inv_df = ReportService.get_inventory_dataframe()
    waste_df = ReportService.get_waste_dataframe()

    db = SessionLocal()
    try:
        today = datetime.date.today()
        settings = FreshnessService.get_settings(db)
        urgent_days = settings["urgent_threshold_days"]

        active_items = (
            db.query(Inventory)
            .options(joinedload(Inventory.vegetable))
            .filter(Inventory.status == "In Stock", Inventory.current_quantity > 0)
            .all()
        )

        fresh_batches = [i for i in active_items if "FRESH" in str(i.freshness_status).upper() and (i.estimated_use_by_date - today).days > urgent_days]
        medium_batches = [i for i in active_items if "MED" in str(i.freshness_status).upper() and (i.estimated_use_by_date - today).days > urgent_days]
        urgent_batches = [i for i in active_items if "SPOIL" not in str(i.freshness_status).upper() and (i.estimated_use_by_date - today).days <= urgent_days and (i.estimated_use_by_date - today).days >= 0]
        spoiled_batches = [i for i in active_items if "SPOIL" in str(i.freshness_status).upper() or (i.estimated_use_by_date - today).days < 0]
    finally:
        db.close()

    # -------------------------------------------------------------
    # 1. 4 STATUS CATEGORY METRIC CARDS (FRESH, MEDIUM, URGENT, SPOILED)
    # -------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("🟢 FRESH ITEMS", f"{len(fresh_batches)} batches", f"{sum(i.current_quantity for i in fresh_batches):.1f} kg safe", "#10b981", "🥦")
    with col2:
        render_metric_card("🟡 MEDIUM ITEMS", f"{len(medium_batches)} batches", f"{sum(i.current_quantity for i in medium_batches):.1f} kg use soon", "#f59e0b", "🥕")
    with col3:
        render_metric_card("🟠 URGENT ITEMS", f"{len(urgent_batches)} batches", f"{sum(i.current_quantity for i in urgent_batches):.1f} kg within 24h", "#f97316", "⚠️")
    with col4:
        render_metric_card("🔴 SPOILED ITEMS", f"{len(spoiled_batches)} batches", f"{sum(i.current_quantity for i in spoiled_batches):.1f} kg discard", "#ef4444", "🚨")

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # 2. Urgent / Spoiled Alert Banner
    crit_count = len(urgent_batches) + len(spoiled_batches)
    if crit_count > 0:
        alert_text = f"{crit_count} batch(es) require immediate kitchen action: {len(spoiled_batches)} spoiled batch(es) to discard, and {len(urgent_batches)} urgent batch(es) to cook today!"
        render_urgent_alert_banner(crit_count, alert_text)

    # -------------------------------------------------------------
    # 3. "WHAT SHOULD WE COOK FIRST?" (FIFO & Shelf-Life Priority)
    # -------------------------------------------------------------
    st.markdown("### 🍲 WHAT SHOULD WE COOK FIRST? (Priority Engine)")
    st.caption("Automatically prioritized by: 1. Spoiled/Urgent status → 2. Lowest remaining life → 3. Earliest estimated use-by date → 4. Freshness condition.")

    ranked_inventory = FreshnessService.rank_inventory_fifo(active_items)

    if ranked_inventory:
        p_cols = st.columns(min(4, len(ranked_inventory)))
        for idx, item in enumerate(ranked_inventory[:4]):
            days_left = (item.estimated_use_by_date - today).days
            fresh_str = str(item.freshness_status).upper()
            
            if "SPOIL" in fresh_str or days_left < 0:
                p_label = "SPOILED"
                p_color = "#ef4444"
                p_text = f"{item.vegetable.name} — 0 days — SPOILED"
            elif days_left <= urgent_days:
                p_label = "URGENT"
                p_color = "#f97316"
                p_text = f"{item.vegetable.name} — {days_left} day{'s' if days_left != 1 else ''} — URGENT"
            elif "MED" in fresh_str or days_left <= 3:
                p_label = "MEDIUM"
                p_color = "#eab308"
                p_text = f"{item.vegetable.name} — {days_left} days — MEDIUM"
            else:
                p_label = "FRESH"
                p_color = "#10b981"
                p_text = f"{item.vegetable.name} — {days_left} days — FRESH"

            with p_cols[idx]:
                st.markdown(f"""
                <div style="background: rgba(30, 41, 59, 0.85); border-top: 4px solid {p_color}; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 800; font-size: 1.1rem; color: #f8fafc;">{item.vegetable.name}</span>
                        <span style="background: {p_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 700;">{p_label}</span>
                    </div>
                    <div style="margin-top: 6px; font-size: 0.85rem; color: #94a3b8; font-weight: 600;">
                        {p_text}
                    </div>
                    <div style="margin-top: 8px; font-size: 0.95rem; color: #cbd5e1;">
                        Stock: <strong>{item.current_quantity} {item.unit}</strong>
                    </div>
                    <div style="font-size: 0.8rem; color: {'#fca5a5' if days_left <= urgent_days else '#fde68a' if days_left <= 3 else '#86efac'}; margin-top: 4px;">
                        ⏳ <strong>{max(0, days_left)} days left</strong> (Use by {item.estimated_use_by_date.strftime('%d %b %Y')})
                    </div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">
                        Freshness Condition: <strong style="color: {p_color};">{item.freshness_status}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No active vegetable inventory in stock. Add or scan new vegetable donations to view cooking recommendations.")

    st.markdown("---")

    # 4. Analytics Visualizations
    st.markdown("### 📊 Inventory & Waste Analytics")
    c1, c2 = st.columns(2)
    with c1:
        fig1 = plot_inventory_by_category(inv_df)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No category data to display.")
    with c2:
        fig2 = plot_freshness_distribution(inv_df)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No freshness data to display.")

    c3, c4 = st.columns(2)
    with c3:
        fig3 = plot_usage_vs_waste(metrics)
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = plot_waste_by_reason(waste_df)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No food waste recorded yet.")
