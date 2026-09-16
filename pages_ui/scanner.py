import streamlit as st
import json
import datetime
import pandas as pd
from PIL import Image
from ai.detector import VegetableDetector
from ai.freshness import FreshnessClassifier
from ai.model_manager import ModelManager
from database.database import SessionLocal
from database.models import ScanResult, Vegetable
from services.donation_service import DonationService
from services.freshness_service import FreshnessService
from auth.authentication import get_current_user

def render_scanner():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            📷 AI Multi-Vegetable Scanner &amp; Object Detector
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Upload or capture vegetable batch photos to detect multiple vegetable species concurrently using 
            <strong>YOLOv8 Object Detection</strong>, count individual items, classify per-object freshness, and calculate shelf life.
        </p>
    </div>
    """, unsafe_allow_html=True)

    status = ModelManager.get_model_status()
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if status["custom_detector_available"]:
            st.success(f"🎯 **Detector**: Custom YOLOv8 ({status['custom_detector_path']}) - {status['supported_class_count']} Classes Supported", icon="✅")
        else:
            st.info("💡 **Detector**: Simulation / Demo Mode Active (Custom YOLO model not loaded)", icon="ℹ️")
    with col_m2:
        if status["custom_freshness_available"]:
            st.success(f"🔬 **Freshness AI**: Custom Classifier ({status['custom_freshness_path']})", icon="✅")
        else:
            st.warning("⚠️ **Freshness AI**: Visual Heuristic Active (Custom freshness model not trained yet)", icon="ℹ️")

    # Display Supported Classes expander if detector model present
    with st.expander("ℹ️ Supported AI Vegetable Detector Classes"):
        supported_classes = status.get("supported_classes", [])
        if supported_classes:
            st.write(f"The currently loaded YOLO model is trained to detect **{len(supported_classes)}** classes:")
            st.write(", ".join([f"{c}" for c in supported_classes]))
        else:
            st.info("No custom trained model loaded at models/yolov8/best.pt. Demonstrating multi-object detection capabilities with standard sample classes.")

    tab1, tab2 = st.tabs(["📁 Upload Photo", "📸 Capture Camera Photo"])
    image_input = None

    with tab1:
        uploaded_file = st.file_uploader("Choose vegetable image file", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file:
            image_input = uploaded_file

    with tab2:
        camera_img = st.camera_input("Take photo of vegetable batch")
        if camera_img:
            image_input = camera_img

    if image_input:
        detector = VegetableDetector()

        with st.spinner("Running YOLOv8 Multi-Object Detection & Per-Object Freshness Classification..."):
            det_result = detector.detect(image_input)
            detections = det_result.get("detections", [])
            summary_counts = det_result.get("summary_counts", {})
            total_count = det_result.get("total_count", 0)
            annotated_image = det_result.get("annotated_image", image_input)
            original_image = det_result.get("original_image", image_input)
            is_demo = det_result.get("is_demo", True)

        if is_demo:
            st.warning("⚠️ **DEMO MODE — NOT REAL AI PREDICTION**: No trained custom YOLO weights file found at models/yolov8/best.pt. Showing sample multi-object detection results.", icon="⚠️")

        col_img, col_analysis = st.columns([1.1, 0.9], gap="large")

        with col_img:
            st.markdown("### 🖼️ Scanned Image & Bounding Boxes")
            st.image(annotated_image, caption=f"YOLOv8 Detection Result ({total_count} Objects Identified)", use_container_width=True)

        with col_analysis:
            st.markdown("### 📊 Detection Summary & Counts")
            
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.9); border: 2px solid #3b82f6; border-radius: 14px; padding: 18px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-weight: 800; font-size: 1.1rem; color: #f8fafc;">TOTAL VEGETABLES DETECTED</span>
                    <span style="background: #3b82f6; color: #ffffff; padding: 4px 14px; border-radius: 20px; font-size: 1.2rem; font-weight: 900;">
                        {total_count} Objects
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px;">
            """, unsafe_allow_html=True)

            summary_cards_html = ""
            for veg, cnt in summary_counts.items():
                summary_cards_html += f"""
                <div style="background: rgba(15, 23, 42, 0.6); padding: 8px 12px; border-radius: 8px; text-align: center; border-left: 3px solid #3b82f6;">
                    <div style="font-size: 0.85rem; color: #94a3b8;">{veg}</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: #f8fafc;">× {cnt}</div>
                </div>
                """
            st.markdown(summary_cards_html + "</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        # -------------------------------------------------------------
        # INDIVIDUAL DETECTIONS TABLE WITH PER-OBJECT LIFE CALCULATIONS
        # -------------------------------------------------------------
        st.markdown("### 📋 Individual Object Detection Analysis")
        today_date = datetime.date.today()
        
        table_rows = []
        for idx, det in enumerate(detections, 1):
            veg_name = det["name"]
            conf_pct = int(round(det["confidence"] * 100))
            freshness = det["freshness"]
            
            calc = FreshnessService.calculate_life_and_use_by(
                vegetable_name=veg_name,
                freshness=freshness,
                received_date=today_date
            )
            
            table_rows.append({
                "#": idx,
                "Vegetable": veg_name,
                "Confidence": f"{conf_pct}%",
                "Freshness": freshness,
                "Configured Shelf Life": f"{calc['configured_shelf_life']} days",
                "Multiplier": f"{calc['multiplier_pct']}%",
                "Est. Remaining Life": f"{calc['effective_remaining_life']} days",
                "Est. Use-By Date": calc['estimated_use_by_date'].strftime('%Y-%m-%d'),
                "Status": calc['status']
            })

        if table_rows:
            df_det = pd.DataFrame(table_rows)
            st.dataframe(df_det, use_container_width=True)

        st.markdown("---")

        # -------------------------------------------------------------
        # MULTI-ITEM CONFIRMATION & INVENTORY ADDITION FORM
        # -------------------------------------------------------------
        st.markdown("### 📥 Confirm & Record Batch Inventory Entries")
        st.info("The scanner has grouped detected items by vegetable class. Adjust quantities and click Confirm to record separate inventory entries for each vegetable type.")

        with st.form("confirm_multi_scan_form"):
            user_donor = st.text_input("Donor / Source Name", value="Community Citizen Donation")
            user_storage = st.selectbox("Storage Condition", ["Room Temperature", "Refrigerated", "Cool & Dark"])
            
            st.markdown("#### Quantities by Vegetable Class")
            veg_form_cols = st.columns(min(3, max(1, len(summary_counts))))
            
            qty_inputs = {}
            fresh_inputs = {}

            for idx, (v_name, count_val) in enumerate(summary_counts.items()):
                col = veg_form_cols[idx % len(veg_form_cols)]
                with col:
                    st.markdown(f"**{v_name}** (Detected: {count_val})")
                    q_val = st.number_input(f"Quantity for {v_name}", min_value=0.1, value=float(count_val), step=0.5, key=f"qty_{v_name}")
                    # Find predominant freshness detected for this veg
                    veg_freshnesses = [d["freshness"] for d in detections if d["name"] == v_name]
                    pred_fresh = max(set(veg_freshnesses), key=veg_freshnesses.count) if veg_freshnesses else "FRESH"
                    f_val = st.selectbox(f"Freshness for {v_name}", ["FRESH", "MEDIUM", "SPOILED"], index=["FRESH", "MEDIUM", "SPOILED"].index(pred_fresh), key=f"fresh_{v_name}")
                    
                    qty_inputs[v_name] = q_val
                    fresh_inputs[v_name] = f_val

            submit_multi = st.form_submit_button("✅ CONFIRM ALL & ADD TO LIVE INVENTORY", use_container_width=True)

            if submit_multi:
                user = get_current_user()
                user_id = user["id"] if user else None
                success_count = 0
                messages = []

                for v_name, qty_val in qty_inputs.items():
                    f_val = fresh_inputs[v_name]
                    ok, msg, don_obj = DonationService.add_donation(
                        donor_name=user_donor,
                        vegetable_name_or_id=v_name,
                        quantity=qty_val,
                        unit="kg",
                        freshness_status=f_val,
                        storage_condition=user_storage,
                        donation_date=today_date,
                        notes=f"AI Scan Batch ({total_count} total detected objects)",
                        user_id=user_id
                    )
                    if ok:
                        success_count += 1
                        messages.append(f"• **{v_name}**: {qty_val} kg added as {f_val}")

                if success_count > 0:
                    # Save scan log
                    db_s = SessionLocal()
                    try:
                        scan = ScanResult(
                            user_id=user_id,
                            image_path="scanned_multi_photo",
                            detected_vegetables_json=json.dumps(list(summary_counts.keys())),
                            confidence_scores_json=json.dumps([d["confidence"] for d in detections]),
                            freshness_estimate=str(dict(fresh_inputs))
                        )
                        db_s.add(scan)
                        db_s.commit()
                    finally:
                        db_s.close()

                    st.success(f"🎉 Successfully recorded **{success_count}** vegetable batch entries into live inventory!\n\n" + "\n".join(messages))
                    st.balloons()
