import streamlit as st
import pandas as pd
from services.report_service import ReportService
from services.waste_service import WasteService

def render_reports():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            📊 Reports & Data Export
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Export complete datasets in CSV format for audits, community reports, and research reviews.
        </p>
    </div>
    """, unsafe_allow_html=True)

    metrics = WasteService.get_waste_metrics()
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px; margin-bottom: 24px;">
        <h4 style="margin: 0 0 10px 0; color: #10b981;">Executive Summary — Santhi Welfare Children Home Food Management</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
            <div>Total Donations: <strong>{metrics['total_donations_count']} batches</strong></div>
            <div>Total Donated Quantity: <strong>{metrics['total_donated_qty']} kg</strong></div>
            <div>Total Quantity Used: <strong>{metrics['total_used_qty']} kg</strong></div>
            <div>Total Quantity Wasted: <strong>{metrics['total_wasted_qty']} kg</strong></div>
            <div>Waste Percentage: <strong>{metrics['waste_percentage']}%</strong></div>
            <div>Utilization Rate: <strong>{metrics['utilization_rate']}%</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📦 Donations Report", "📋 Inventory Report", "🍲 Usage Report", "🗑️ Waste Report"])

    with tab1:
        st.markdown("### Donations Report")
        df_don = ReportService.get_donations_dataframe()
        if not df_don.empty:
            st.dataframe(df_don, use_container_width=True)
            csv_don = df_don.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Donations CSV", data=csv_don, file_name="nourishai_donations_report.csv", mime="text/csv")
        else:
            st.info("No donation data available.")

    with tab2:
        st.markdown("### Inventory Report")
        df_inv = ReportService.get_inventory_dataframe()
        if not df_inv.empty:
            st.dataframe(df_inv, use_container_width=True)
            csv_inv = df_inv.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Inventory CSV", data=csv_inv, file_name="nourishai_inventory_report.csv", mime="text/csv")
        else:
            st.info("No inventory data available.")

    with tab3:
        st.markdown("### Food Usage Report")
        df_use = ReportService.get_usage_dataframe()
        if not df_use.empty:
            st.dataframe(df_use, use_container_width=True)
            csv_use = df_use.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Usage CSV", data=csv_use, file_name="nourishai_usage_report.csv", mime="text/csv")
        else:
            st.info("No usage records available.")

    with tab4:
        st.markdown("### Food Waste Report")
        df_wst = ReportService.get_waste_dataframe()
        if not df_wst.empty:
            st.dataframe(df_wst, use_container_width=True)
            csv_wst = df_wst.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Waste CSV", data=csv_wst, file_name="nourishai_waste_report.csv", mime="text/csv")
        else:
            st.info("No waste records available.")
