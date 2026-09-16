# NourishAI — Multi-Vegetable YOLOv8 Training & Annotation Guide

## 1. Dataset Structure
Organize your annotated images and YOLO label text files in dataset/:

`
dataset/
├── data.yaml
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
`

## 2. Multi-Object Bounding Box Annotation
Every individual vegetable in an image must have its own bounding box annotation line in standard YOLO format:
<class_id> <x_center> <y_center> <width> <height>

Example image with 4 Tomatoes and 3 Carrots:
- Image contains 7 bounding boxes
- Corresponding .txt file in dataset/labels/train/ contains 7 lines.

## 3. Recommended Free Annotation Tools
- **Roboflow Universe** (Search 'vegetable object detection' for thousands of ready-annotated images)
- **LabelImg** or **CVAT** (For manual box drawing)

## 4. Run Training
`ash
python scripts/train.py --epochs 50 --batch 16 --weights yolov8n.pt
`

After training, the best weights are saved to models/yolov8/best.pt.
NourishAI will automatically load the model and dynamically read model.names!
