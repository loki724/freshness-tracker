import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOM_DETECTOR_PATH = os.path.join(BASE_DIR, "models", "yolov8", "best.pt")
CUSTOM_FRESHNESS_PATH = os.path.join(BASE_DIR, "models", "freshness", "best.pt")

_cached_detector_classes = None

class ModelManager:
    @staticmethod
    def get_supported_classes() -> list:
        global _cached_detector_classes
        if _cached_detector_classes is not None:
            return _cached_detector_classes
        
        has_detector = os.path.exists(CUSTOM_DETECTOR_PATH)
        if has_detector:
            try:
                from ultralytics import YOLO
                m = YOLO(CUSTOM_DETECTOR_PATH)
                if hasattr(m, "names") and m.names:
                    classes = [str(name).strip().title() for idx, name in sorted(m.names.items())]
                    _cached_detector_classes = classes
                    return classes
            except Exception as e:
                print(f"Notice reading YOLO model classes: {e}")
        
        _cached_detector_classes = []
        return []

    @staticmethod
    def get_model_status():
        has_detector = os.path.exists(CUSTOM_DETECTOR_PATH)
        has_freshness = os.path.exists(CUSTOM_FRESHNESS_PATH)
        supported_classes = ModelManager.get_supported_classes()
        class_count = len(supported_classes)
        
        return {
            "custom_detector_available": has_detector,
            "custom_detector_path": CUSTOM_DETECTOR_PATH,
            "custom_freshness_available": has_freshness,
            "custom_freshness_path": CUSTOM_FRESHNESS_PATH,
            "custom_model_available": has_detector,
            "custom_model_path": CUSTOM_DETECTOR_PATH,
            "detector_mode": "Trained Custom YOLOv8" if has_detector else "Intelligent Fallback / Demonstration Mode",
            "freshness_mode": "Trained Freshness AI Model" if has_freshness else "Freshness AI model is not trained/installed yet (Heuristic / Manual Inspection Active)",
            "supported_classes": supported_classes,
            "supported_class_count": class_count,
            "description": (
                f"Custom YOLO detector: {'Loaded (' + str(class_count) + ' classes)' if has_detector else 'Not present'} | Freshness model: {'Loaded' if has_freshness else 'Not trained/installed yet'}"
            )
        }

    @staticmethod
    def load_detector():
        from ai.detector import VegetableDetector
        return VegetableDetector()

    @staticmethod
    def load_freshness_classifier():
        from ai.freshness import FreshnessClassifier
        return FreshnessClassifier()
