import streamlit as st
import datetime
from database.database import SessionLocal
from database.models import Vegetable
from services.freshness_service import FreshnessService
from services.alert_service import AlertService
from ai.model_manager import ModelManager

def render_settings():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            ⚙️ System &amp; AI Configuration
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Central single source of truth for vegetable shelf-life values, freshness multipliers, alert thresholds, and AI detector settings.
        </p>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        current_settings = FreshnessService.get_settings(db)
        vegetables = db.query(Vegetable).all()
        tomato_veg = next((v for v in vegetables if v.name.upper() == "TOMATO"), None)
        tomato_days = tomato_veg.default_shelf_life_days if tomato_veg else 7
    finally:
        db.close()

    if "settings_just_saved" in st.session_state and st.session_state["settings_just_saved"]:
        st.success("✅ Settings saved successfully to database! All subsequent calculations, scanner results, and alerts will use these new settings.")
        st.session_state["settings_just_saved"] = False

    tab1, tab2, tab3 = st.tabs(["🌱 Freshness Multipliers & Thresholds", "🥕 Vegetable Shelf-Life Rules", "🎯 AI Object Detector Settings"])

    with tab1:
        st.markdown("### 🎛️ Configure Freshness Multipliers & Alert Ranges")
        st.caption("These multipliers and thresholds govern effective life calculation and alert generation across the entire system.")
        
        with st.form("multipliers_and_thresholds_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                fresh_pct = st.number_input(
                    "🟢 Fresh Multiplier (%)",
                    min_value=50, max_value=150,
                    value=current_settings["fresh_multiplier_pct"],
                    step=5,
                    help="Percentage of configured shelf life for Fresh condition (Default: 100%)"
                )
            with c2:
                medium_pct = st.number_input(
                    "🟡 Medium Multiplier (%)",
                    min_value=10, max_value=80,
                    value=current_settings["medium_multiplier_pct"],
                    step=5,
                    help="Percentage of configured shelf life for Medium condition (Default: 40%)"
                )
            with c3:
                spoiled_pct = st.number_input(
                    "🔴 Spoiled Multiplier (%)",
                    min_value=0, max_value=20,
                    value=current_settings["spoiled_multiplier_pct"],
                    step=5,
                    help="Percentage for Spoiled condition (Default: 0% = 0 days)"
                )

            st.markdown("---")
            st.markdown("#### 🚨 Alert Threshold Rules")
            a1, a2 = st.columns(2)
            with a1:
                urgent_val = st.number_input(
                    "🟠 Urgent Alert Threshold (Days Remaining ≤)",
                    min_value=0, max_value=3,
                    value=current_settings["urgent_threshold_days"],
                    step=1,
                    help="Batches with days remaining less than or equal to this trigger an URGENT alert (e.g. 0-1 days)"
                )
            with a2:
                use_soon_val = st.number_input(
                    "🟡 Use Soon Alert Threshold (Days Remaining ≤)",
                    min_value=1, max_value=7,
                    value=current_settings["use_soon_threshold_days"],
                    step=1,
                    help="Batches with days remaining less than or equal to this trigger a USE SOON alert (e.g. 2-3 days)"
                )

            st.markdown("---")
            org_input = st.text_input("Beneficiary Organization Name", value=current_settings["org_name"])

            submit_settings = st.form_submit_button("💾 SAVE SETTINGS", use_container_width=True)

            if submit_settings:
                new_settings = {
                    "fresh_multiplier": str(fresh_pct / 100.0),
                    "medium_multiplier": str(medium_pct / 100.0),
                    "spoiled_multiplier": str(spoiled_pct / 100.0),
                    "urgent_threshold_days": str(urgent_val),
                    "use_soon_threshold_days": str(use_soon_val),
                    "org_name": org_input
                }
                ok = FreshnessService.save_settings(new_settings)
                if ok:
                    AlertService.sync_inventory_alerts()
                    st.session_state["settings_just_saved"] = True
                    st.rerun()
                else:
                    st.error("Failed to save settings to database.")

    with tab2:
        st.markdown("### 🥕 Configurable Default Shelf-Life Days per Vegetable")
        st.caption("Base shelf-life values used as the baseline before applying freshness condition multipliers.")

        with st.form("vegetable_shelf_lives_form"):
            veg_shelf_inputs = {}
            cols = st.columns(2)
            for idx, v in enumerate(vegetables):
                with cols[idx % 2]:
                    veg_shelf_inputs[v.id] = st.number_input(
                        f"{v.name} ({v.category}) — Base Days",
                        min_value=1,
                        max_value=90,
                        value=v.default_shelf_life_days or 7,
                        key=f"v_shelf_{v.id}"
                    )
            
            submit_vegs = st.form_submit_button("💾 SAVE VEGETABLE SHELF LIVES", use_container_width=True)
            if submit_vegs:
                db_veg = SessionLocal()
                try:
                    for v_id, days in veg_shelf_inputs.items():
                        veg_obj = db_veg.query(Vegetable).filter(Vegetable.id == v_id).first()
                        if veg_obj:
                            veg_obj.default_shelf_life_days = days
                    db_veg.commit()
                    FreshnessService.save_settings({}, db=db_veg)
                    AlertService.sync_inventory_alerts(db_veg)
                    st.session_state["settings_just_saved"] = True
                finally:
                    db_veg.close()
                st.rerun()

    with tab3:
        st.markdown("### 🎯 AI Detector Thresholds & Model Capabilities")
        st.caption("Configure YOLO object detection parameters and inspect supported vegetable classes.")

        model_info = ModelManager.get_model_status()
        
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.8); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 14px; margin-bottom: 20px;">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem;">🤖 Active AI Model Information</div>
            <div style="color: #cbd5e1; font-size: 0.9rem; margin-top: 4px;">
                Mode: <strong>{model_info['detector_mode']}</strong><br/>
                Weights Path: <code>{model_info['custom_detector_path']}</code><br/>
                Supported Vegetable Classes: <strong>{model_info['supported_class_count']} classes</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("ai_thresholds_form"):
            c_conf, c_iou = st.columns(2)
            with c_conf:
                conf_val_pct = st.slider(
                    "Confidence Threshold (%)",
                    min_value=10, max_value=95,
                    value=current_settings.get("confidence_threshold_pct", 50),
                    step=5,
                    help="Detections below this score are filtered out as low-confidence."
                )
            with c_iou:
                iou_val_pct = st.slider(
                    "IoU / NMS Suppression Threshold (%)",
                    min_value=10, max_value=80,
                    value=current_settings.get("iou_threshold_pct", 45),
                    step=5,
                    help="Controls overlap suppression to prevent duplicate bounding boxes for the same vegetable object."
                )

            submit_ai = st.form_submit_button("💾 SAVE AI THRESHOLDS", use_container_width=True)
            if submit_ai:
                ai_settings = {
                    "confidence_threshold": str(conf_val_pct / 100.0),
                    "iou_threshold": str(iou_val_pct / 100.0)
                }
                ok = FreshnessService.save_settings(ai_settings)
                if ok:
                    st.session_state["settings_just_saved"] = True
                    st.rerun()

        st.markdown("#### 📋 Dynamically Loaded Supported Vegetable Classes")
        sup_classes = model_info.get("supported_classes", [])
        if sup_classes:
            st.write(f"The loaded YOLO model ({model_info['custom_detector_path']}) specifies these **{len(sup_classes)}** classes in its model.names metadata:")
            st.write(", ".join([f"{c}" for c in sup_classes]))
        else:
            st.info("No custom trained model file is present at models/yolov8/best.pt. The AI Scanner is currently operating in Demonstration Mode.")

    # -------------------------------------------------------------
    # LAST SAVED SETTINGS DISPLAY (Prominent & Real-time from DB)
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📋 LAST SAVED SETTINGS (Active Database Configuration)")
    
    latest = FreshnessService.get_settings()
    db_check = SessionLocal()
    try:
        t_obj = db_check.query(Vegetable).filter(Vegetable.name.ilike("Tomato")).first()
        t_days = t_obj.default_shelf_life_days if t_obj else 7
    finally:
        db_check.close()

    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 20px; margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 14px;">
            <span style="color: #10b981; font-weight: 700; font-size: 1.05rem;">🔒 Current Single Source of Truth</span>
            <span style="color: #94a3b8; font-size: 0.85rem;">Last Updated: <strong style="color: #f8fafc;">{latest['last_updated']}</strong></span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px;">
            <div><span style="color: #94a3b8;">Organization:</span><br/><strong style="color: #f8fafc; font-size: 1.05rem;">{latest['org_name']}</strong></div>
            <div><span style="color: #94a3b8;">Tomato Shelf Life:</span><br/><strong style="color: #f8fafc; font-size: 1.05rem;">{t_days} days</strong></div>
            <div><span style="color: #94a3b8;">Fresh Multiplier:</span><br/><strong style="color: #10b981; font-size: 1.05rem;">{latest['fresh_multiplier_pct']}%</strong></div>
            <div><span style="color: #94a3b8;">Medium Multiplier:</span><br/><strong style="color: #f59e0b; font-size: 1.05rem;">{latest['medium_multiplier_pct']}%</strong></div>
            <div><span style="color: #94a3b8;">Spoiled Multiplier:</span><br/><strong style="color: #ef4444; font-size: 1.05rem;">{latest['spoiled_multiplier_pct']}%</strong></div>
            <div><span style="color: #94a3b8;">Confidence Threshold:</span><br/><strong style="color: #3b82f6; font-size: 1.05rem;">{latest['confidence_threshold_pct']}%</strong></div>
            <div><span style="color: #94a3b8;">IoU NMS Threshold:</span><br/><strong style="color: #8b5cf6; font-size: 1.05rem;">{latest['iou_threshold_pct']}%</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
