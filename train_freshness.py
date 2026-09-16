import argparse
import os

def train_freshness_model(data_dir="dataset/freshness", epochs=30, imgsz=224, batch=16, model_type="yolov8n-cls.pt"):
    """
    Train a custom Freshness Classification Model on 3 classes: Fresh, Medium, Spoiled.
    Exports the resulting weights to models/freshness/best.pt.
    """
    print("=" * 60)
    print("🌱 NourishAI — Freshness Classification Training Pipeline")
    print("=" * 60)
    print(f"Dataset Directory: {data_dir}")
    print(f"Classes: FRESH, MEDIUM, SPOILED")
    print(f"Epochs: {epochs}")
    print(f"Image Size: {imgsz}x{imgsz}")
    print(f"Batch Size: {batch}")
    print(f"Base Model: {model_type}")
    print("=" * 60)

    try:
        from ultralytics import YOLO
        
        # Load classification base model
        model = YOLO(model_type)
        
        # Train classifier
        results = model.train(
            data=data_dir,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            project="runs/classify",
            name="nourishai_freshness_train"
        )
        
        export_target = "models/freshness/best.pt"
        os.makedirs(os.path.dirname(export_target), exist_ok=True)
        print(f"\nFreshness training completed successfully!")
        print(f"Copy the best model weights to: {export_target}")

    except Exception as e:
        print(f"Training error / notice: {e}")
        print("Ensure dataset/freshness/ contains fresh/, medium/, and spoiled/ subfolders with annotated images.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train NourishAI Freshness Classifier")
    parser.add_argument("--data", type=str, default="dataset/freshness", help="Dataset directory")
    parser.add_argument("--epochs", type=int, default=30, help="Training epochs")
    parser.add_argument("--imgsz", type=int, default=224, help="Image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--model", type=str, default="yolov8n-cls.pt", help="Pretrained classification weights")
    args = parser.parse_args()

    train_freshness_model(
        data_dir=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        model_type=args.model
    )
