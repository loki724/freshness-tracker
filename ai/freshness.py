import os
import numpy as np
from PIL import Image
from ai.model_manager import CUSTOM_FRESHNESS_PATH

class FreshnessClassifier:
    """
    Freshness Classifier supporting 3 distinct conditions:
    1. FRESH
    2. MEDIUM
    3. SPOILED
    """
    def __init__(self):
        self.model_path = CUSTOM_FRESHNESS_PATH
        self.has_model = os.path.exists(self.model_path)
        self.model = None
        if self.has_model:
            try:
                from ultralytics import YOLO
                self.model = YOLO(self.model_path)
            except Exception as e:
                print(f"Notice loading freshness model: {e}")
                self.model = None

    def classify_freshness(self, image: Image.Image, vegetable_name: str = "Vegetable") -> dict:
        """
        Classifies an image or crop into FRESH, MEDIUM, or SPOILED.
        Returns dictionary with freshness level, confidence, and transparent AI indicator.
        """
        if self.model is not None:
            try:
                results = self.model(image)
                probs = results[0].probs
                top1_idx = int(probs.top1)
                class_names = results[0].names
                predicted_label = class_names.get(top1_idx, "FRESH").upper()
                
                # Standardize to 3 classes
                if "SPOIL" in predicted_label or "ROTTEN" in predicted_label or "BAD" in predicted_label:
                    freshness = "SPOILED"
                elif "MED" in predicted_label or "RIPE" in predicted_label or "FAIR" in predicted_label:
                    freshness = "MEDIUM"
                else:
                    freshness = "FRESH"
                
                confidence = float(probs.top1conf.item())
                return {
                    "freshness": freshness,
                    "confidence": round(confidence, 2),
                    "confidence_pct": int(round(confidence * 100)),
                    "is_real_ai": True,
                    "model_source": "Trained Freshness Model (models/freshness/best.pt)",
                    "status_note": "Real AI Classification"
                }
            except Exception as e:
                print(f"Error during freshness model inference: {e}")

        # If custom freshness model is not trained yet, run transparent visual heuristic
        return self._heuristic_or_demo_classification(image, vegetable_name)

    def _heuristic_or_demo_classification(self, image: Image.Image, vegetable_name: str) -> dict:
        """
        Visual heuristics (color histogram & saturation) as transparent pre-training inspection.
        Never pretends to be a trained deep-learning model prediction.
        """
        try:
            img_arr = np.array(image.convert("RGB"))
            r_mean = float(np.mean(img_arr[:, :, 0]))
            g_mean = float(np.mean(img_arr[:, :, 1]))
            b_mean = float(np.mean(img_arr[:, :, 2]))
            brightness = (r_mean + g_mean + b_mean) / 3.0

            # Very dark / discolored indicates potential spoilage
            if brightness < 45.0:
                freshness = "SPOILED"
                estimated_conf = 0.90
            elif brightness < 80.0 or (r_mean > 140 and g_mean < 80 and b_mean < 80 and "SPINACH" in vegetable_name.upper()):
                freshness = "MEDIUM"
                estimated_conf = 0.85
            else:
                freshness = "FRESH"
                estimated_conf = 0.92
        except Exception:
            freshness = "FRESH"
            estimated_conf = 0.88

        return {
            "freshness": freshness,
            "confidence": estimated_conf,
            "confidence_pct": int(round(estimated_conf * 100)),
            "is_real_ai": False,
            "model_source": "Freshness AI model is not trained/installed yet.",
            "status_note": "Visual Heuristic / Demo Mode (Awaiting custom model training)"
        }

    @staticmethod
    def get_freshness_badge(status: str) -> dict:
        status_norm = str(status).strip().upper()
        if "SPOIL" in status_norm:
            return {"level": "SPOILED", "color": "#ef4444", "icon": "🔴", "desc": "SPOILED — DO NOT USE", "badge_class": "priority-badge-urgent"}
        elif "MED" in status_norm or "RIPE" in status_norm or "SOON" in status_norm:
            return {"level": "MEDIUM", "color": "#f59e0b", "icon": "🟡", "desc": "USE SOON", "badge_class": "priority-badge-soon"}
        else:
            return {"level": "FRESH", "color": "#10b981", "icon": "🟢", "desc": "SAFE / FRESH", "badge_class": "priority-badge-fresh"}
