import argparse
import os
import shutil

def train_yolov8_model(data_yaml="dataset/data.yaml", epochs=50, img_size=640, batch_size=16, model_name="yolov8n.pt", device=None):
    \"\"\"
    Train a custom YOLOv8 object detection model for multi-vegetable identification.
    \"\"\"
    print("=" * 65)
    print("🌱 NourishAI — Broad Vegetable Object Detection Training Pipeline")
    print("=" * 65)
    print(f"Dataset YAML: {data_yaml}")
    print(f"Epochs: {epochs}")
    print(f"Resolution: {img_size}x{img_size}")
    print(f"Batch Size: {batch_size}")
    print(f"Base Pretrained Weights: {model_name}")
    print("=" * 65)

    try:
        from ultralytics import YOLO
        
        # Load base pretrained model
        model = YOLO(model_name)
        
        # Train model
        train_args = {
            "data": data_yaml,
            "epochs": epochs,
            "imgsz": img_size,
            "batch": batch_size,
            "plots": True,
            "save": True,
            "project": "runs/detect",
            "name": "nourishai_yolo_train"
        }
        if device:
            train_args["device"] = device

        results = model.train(**train_args)
        
        print("\n🎉 Training completed successfully!")
        
        # Copy best.pt to target model path
        export_target = os.path.join("models", "yolov8", "best.pt")
        os.makedirs(os.path.dirname(export_target), exist_ok=True)
        
        best_weights = os.path.join("runs", "detect", "nourishai_yolo_train", "weights", "best.pt")
        if os.path.exists(best_weights):
            shutil.copy(best_weights, export_target)
            print(f"✅ Trained weights automatically saved to: {export_target}")
        else:
            print(f"💡 Copy best weights to: {export_target}")
        
    except ImportError:
        print("❌ Ultralytics package is required. Install via: pip install ultralytics")
    except Exception as e:
        print(f"❌ Training failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train custom YOLOv8 object detector for NourishAI")
    parser.add_argument("--data", type=str, default="dataset/data.yaml", help="Path to data.yaml")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--weights", type=str, default="yolov8n.pt", help="Pretrained weights")
    parser.add_argument("--device", type=str, default=None, help="Device (cpu, 0, 1, cuda)")
    args = parser.parse_args()

    train_yolov8_model(
        data_yaml=args.data,
        epochs=args.epochs,
        img_size=args.imgsz,
        batch_size=args.batch,
        model_name=args.weights,
        device=args.device
    )
