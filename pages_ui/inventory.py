import streamlit as st
import datetime
from sqlalchemy.orm import joinedload
from database.database import SessionLocal
from database.models import Inventory
from services.freshness_service import FreshnessService
from services.report_service import ReportService


def render_inventory():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            📦 Live Vegetable Inventory &amp; FIFO Priority
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Real-time stock levels with automatic priority tracking and First-In-First-Out (FIFO) cooking recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        today = datetime.date.today()
        items = (
            db.query(Inventory)
            .options(joinedload(Inventory.vegetable))
            .filter(Inventory.status == "In Stock")
            .all()
        )
        ranked_items = FreshnessService.rank_inventory_fifo(items)
    finally:
        db.close()

    # --- FIFO Recommendation Section ---
    st.markdown("### 🍳 Recommended Cooking Order (Priority Engine)")
    if ranked_items:
        cols = st.columns(min(3, len(ranked_items)))
        for i, item in enumerate(ranked_items[:3]):
            days_left = (item.estimated_use_by_date - today).days
            priority_label, _, _, color = FreshnessService.calculate_priority_and_status(
                item.estimated_use_by_date, today
            )
            fresh_status = str(item.freshness_status).upper()

            if "SPOIL" in fresh_status or days_left < 0:
                badge_icon = "🔴"
                status_label = "SPOILED"
                status_color = "#ef4444"
            elif days_left <= 1:
                badge_icon = "🟠"
                status_label = "URGENT"
                status_color = "#f97316"
            elif days_left <= 3:
                badge_icon = "🟡"
                status_label = "USE SOON"
                status_color = "#eab308"
            else:
                badge_icon = "🟢"
                status_label = "FRESH"
                status_color = "#10b981"

            effective_life = item.effective_life_days
            mult = item.multiplier_used
            eff_text = f"{effective_life}d effective life" if effective_life is not None else ""
            mult_pct = f" ({int(mult * 100)}pct multiplier)" if mult is not None else ""

            with cols[i]:
                eff_html = (
                    f'<div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">📐 {eff_text}{mult_pct}</div>'
                    if eff_text else ""
                )
                days_color = "#fca5a5" if days_left <= 2 else "#fde68a" if days_left <= 5 else "#86efac"
                st.markdown(f"""
                <div style="background: rgba(30, 41, 59, 0.9); border-top: 4px solid {status_color}; border-radius: 12px; padding: 16px; margin-bottom: 8px;">
                    <div style="font-size: 0.8rem; color: {status_color}; font-weight: 700; text-transform: uppercase;">
                        {badge_icon} RANK #{i+1} — {status_label}
                    </div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #f8fafc; margin-top: 4px;">{item.vegetable.name}</div>
                    <div style="color: #cbd5e1; font-size: 0.95rem; margin-top: 6px;">
                        Stock: <strong>{item.current_quantity} {item.unit}</strong>
                    </div>
                    <div style="font-size: 0.85rem; color: {days_color}; margin-top: 4px;">
                        ⏳ <strong>{days_left} days remaining</strong> (Use by {item.estimated_use_by_date})
                    </div>
                    {eff_html}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No active inventory in stock.")

    st.markdown("---")

    # --- Filterable Inventory Table ---
    st.markdown("### 📋 Current Inventory Table")
    df = ReportService.get_inventory_dataframe()

    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1:
            cat_filter = st.multiselect(
                "Filter by Category",
                options=df["Category"].unique(),
                default=list(df["Category"].unique())
            )
        with c2:
            fresh_opts = df["Freshness Condition"].unique().tolist()
            fresh_filter = st.multiselect(
                "Filter by Freshness",
                options=fresh_opts,
                default=fresh_opts
            )
        with c3:
            sort_by = st.selectbox(
                "Sort By",
                ["Days Remaining (Urgent First)", "Received Date (Oldest First)", "Current Qty (Highest First)"]
            )

        filtered = df[
            df["Category"].isin(cat_filter) &
            df["Freshness Condition"].isin(fresh_filter)
        ]

        if sort_by == "Days Remaining (Urgent First)":
            filtered = filtered.sort_values(by="Days Remaining", ascending=True)
        elif sort_by == "Received Date (Oldest First)":
            filtered = filtered.sort_values(by="Received Date", ascending=True)
        elif sort_by == "Current Qty (Highest First)":
            filtered = filtered.sort_values(by="Current Qty", ascending=False)

        st.markdown("""
        <div style="display:flex; gap:16px; margin-bottom:8px; flex-wrap:wrap;">
            <span style="font-size:0.82rem; color:#10b981;">🟢 FRESH — Safe to use</span>
            <span style="font-size:0.82rem; color:#eab308;">🟡 MEDIUM — Use soon</span>
            <span style="font-size:0.82rem; color:#f97316;">🟠 URGENT — Use within 24 h</span>
            <span style="font-size:0.82rem; color:#ef4444;">🔴 SPOILED — Do not use</span>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("Inventory is empty.")
