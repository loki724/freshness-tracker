import os
import random
from collections import Counter
from PIL import Image
from ai.model_manager import ModelManager, CUSTOM_DETECTOR_PATH as CUSTOM_MODEL_PATH
from ai.freshness import FreshnessClassifier
from ai.preprocessing import load_image, draw_detections
from services.freshness_service import FreshnessService

class VegetableDetector:
    def __init__(self):
        self.status = ModelManager.get_model_status()
        self.model = None
        if self.status["custom_model_available"]:
            try:
                from ultralytics import YOLO
                self.model = YOLO(CUSTOM_MODEL_PATH)
            except Exception as e:
                print(f"Error loading custom YOLOv8 model: {e}")
                self.model = None

    def detect(self, image_input, conf_threshold: float = None, iou_threshold: float = None) -> dict:
        image = load_image(image_input)
        
        settings = FreshnessService.get_settings()
        if conf_threshold is None:
            conf_threshold = settings.get("confidence_threshold", 0.50)
        if iou_threshold is None:
            iou_threshold = settings.get("iou_threshold", 0.45)

        fresh_classifier = FreshnessClassifier()

        # If custom model weights exist
        if self.model is not None:
            try:
                results = self.model(image, conf=conf_threshold, iou=iou_threshold)
                detections = []
                w, h = image.size

                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        cls_name = r.names.get(cls_id, f"Veg_{cls_id}").strip().title()
                        conf = float(box.conf[0].item())
                        coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

                        # Crop individual object for freshness classification
                        xmin, ymin, xmax, ymax = max(0, int(coords[0])), max(0, int(coords[1])), min(w, int(coords[2])), min(h, int(coords[3]))
                        crop = image.crop((xmin, ymin, xmax, ymax)) if (xmax > xmin and ymax > ymin) else image
                        
                        fresh_res = fresh_classifier.classify_freshness(crop, cls_name)
                        freshness = fresh_res["freshness"]

                        detections.append({
                            "name": cls_name,
                            "confidence": round(conf, 2),
                            "box": [coords[0]/w, coords[1]/h, coords[2]/w, coords[3]/h],
                            "pixel_box": [xmin, ymin, xmax, ymax],
                            "freshness": freshness,
                            "freshness_conf": fresh_res["confidence"]
                        })

                counts = Counter([d["name"] for d in detections])
                annotated_img = draw_detections(image, detections)
                return {
                    "is_demo": False,
                    "detections": detections,
                    "summary_counts": dict(counts),
                    "total_count": len(detections),
                    "annotated_image": annotated_img,
                    "original_image": image
                }
            except Exception as e:
                print(f"Inference error with custom model: {e}. Falling back to demo mode.")

        # Fallback Demonstration Mode (clearly labeled)
        return self._run_demo_detection(image, fresh_classifier)

    def _run_demo_detection(self, image: Image.Image, fresh_classifier: FreshnessClassifier) -> dict:
        # Multi-object sample detections illustrating 17 total items across 6 vegetable classes
        demo_objects = [
            # 4 Tomatoes
            {"name": "Tomato", "confidence": 0.95, "box": [0.05, 0.08, 0.25, 0.35], "freshness": "FRESH"},
            {"name": "Tomato", "confidence": 0.92, "box": [0.28, 0.05, 0.45, 0.32], "freshness": "FRESH"},
            {"name": "Tomato", "confidence": 0.89, "box": [0.08, 0.38, 0.26, 0.62], "freshness": "MEDIUM"},
            {"name": "Tomato", "confidence": 0.86, "box": [0.29, 0.36, 0.46, 0.64], "freshness": "SPOILED"},
            
            # 3 Carrots
            {"name": "Carrot", "confidence": 0.94, "box": [0.50, 0.06, 0.70, 0.40], "freshness": "FRESH"},
            {"name": "Carrot", "confidence": 0.91, "box": [0.72, 0.05, 0.92, 0.38], "freshness": "FRESH"},
            {"name": "Carrot", "confidence": 0.88, "box": [0.52, 0.42, 0.71, 0.72], "freshness": "MEDIUM"},

            # 5 Potatoes
            {"name": "Potato", "confidence": 0.93, "box": [0.05, 0.68, 0.22, 0.92], "freshness": "FRESH"},
            {"name": "Potato", "confidence": 0.90, "box": [0.24, 0.67, 0.40, 0.91], "freshness": "FRESH"},
            {"name": "Potato", "confidence": 0.87, "box": [0.42, 0.68, 0.58, 0.92], "freshness": "FRESH"},
            {"name": "Potato", "confidence": 0.85, "box": [0.60, 0.69, 0.76, 0.93], "freshness": "MEDIUM"},
            {"name": "Potato", "confidence": 0.82, "box": [0.78, 0.68, 0.95, 0.92], "freshness": "MEDIUM"},

            # 2 Onions
            {"name": "Onion", "confidence": 0.91, "box": [0.74, 0.40, 0.88, 0.65], "freshness": "FRESH"},
            {"name": "Onion", "confidence": 0.89, "box": [0.85, 0.38, 0.98, 0.62], "freshness": "FRESH"},

            # 1 Cabbage
            {"name": "Cabbage", "confidence": 0.96, "box": [0.48, 0.70, 0.62, 0.92], "freshness": "FRESH"},

            # 2 Brinjals
            {"name": "Brinjal", "confidence": 0.90, "box": [0.65, 0.45, 0.78, 0.68], "freshness": "FRESH"},
            {"name": "Brinjal", "confidence": 0.87, "box": [0.78, 0.46, 0.90, 0.70], "freshness": "MEDIUM"}
        ]

        counts = Counter([d["name"] for d in demo_objects])
        annotated_img = draw_detections(image, demo_objects)

        return {
            "is_demo": True,
            "detections": demo_objects,
            "summary_counts": dict(counts),
            "total_count": len(demo_objects),
            "annotated_image": annotated_img,
            "original_image": image
        }
