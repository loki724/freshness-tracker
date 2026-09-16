import os
import cv2
import numpy as np
from PIL import Image, ImageDraw

def load_image(image_input):
    if isinstance(image_input, (str, os.PathLike)):
        return Image.open(image_input).convert("RGB")
    elif isinstance(image_input, bytes):
        import io
        return Image.open(io.BytesIO(image_input)).convert("RGB")
    elif hasattr(image_input, "read"):
        return Image.open(image_input).convert("RGB")
    elif isinstance(image_input, np.ndarray):
        return Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
    elif isinstance(image_input, Image.Image):
        return image_input.convert("RGB")
    raise ValueError("Unsupported image format")

def draw_detections(image: Image.Image, detections: list) -> Image.Image:
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    width, height = annotated.size

    for det in detections:
        box = det.get("box", [0.1, 0.1, 0.9, 0.9])
        if max(box) <= 1.0:
            xmin = int(box[0] * width)
            ymin = int(box[1] * height)
            xmax = int(box[2] * width)
            ymax = int(box[3] * height)
        else:
            xmin, ymin, xmax, ymax = int(box[0]), int(box[1]), int(box[2]), int(box[3])

        label = det.get("name", "Vegetable")
        conf = det.get("confidence", 0.9)
        freshness = str(det.get("freshness", "FRESH")).upper()

        if "SPOIL" in freshness:
            border_color = "#ef4444"
            fresh_label = "SPOILED"
        elif "MED" in freshness or "RIPE" in freshness or "SOON" in freshness:
            border_color = "#f59e0b"
            fresh_label = "MEDIUM"
        else:
            border_color = "#10b981"
            fresh_label = "FRESH"

        for i in range(3):
            draw.rectangle([xmin - i, ymin - i, xmax + i, ymax + i], outline=border_color)

        tag = f"{label} ({int(conf * 100)}%) [{fresh_label}]"
        tag_width = len(tag) * 8 + 8
        tag_height = 20
        tag_ymin = max(0, ymin - tag_height)
        
        draw.rectangle([xmin, tag_ymin, xmin + tag_width, tag_ymin + tag_height], fill=border_color)
        draw.text((xmin + 4, tag_ymin + 3), tag, fill="#ffffff")

    return annotated
