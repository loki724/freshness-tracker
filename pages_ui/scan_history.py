import streamlit as st
import json
from database.database import SessionLocal
from database.models import ScanResult

def render_scan_history():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            📜 AI Scan History
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Log of previously executed AI vegetable scans and detection confidence outputs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        scans = db.query(ScanResult).order_by(ScanResult.created_at.desc()).all()
    finally:
        db.close()

    if not scans:
        st.info("No scans recorded yet. Use the **AI Scanner** to upload and detect vegetables.")
    else:
        for scan in scans:
            vegs = json.loads(scan.detected_vegetables_json) if scan.detected_vegetables_json else []
            confs = json.loads(scan.confidence_scores_json) if scan.confidence_scores_json else []
            veg_str = ", ".join(vegs) if vegs else "None"
            
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: #10b981; font-size: 1.05rem;">Scan #{scan.id:04d}</strong>
                    <span style="color: #94a3b8; font-size: 0.8rem;">{scan.created_at.strftime('%Y-%m-%d %H:%M')}</span>
                </div>
                <div style="margin-top: 6px; color: #f8fafc; font-size: 0.95rem;">
                    Detected Vegetables: <strong>{veg_str}</strong>
                </div>
                <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 4px;">
                    Assessed Condition: <span style="color: #10b981;">{scan.freshness_estimate}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
