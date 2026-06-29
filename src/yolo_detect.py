from pathlib import Path
import pandas as pd
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parents[1]
IMAGE_DIR = BASE_DIR / "data" / "raw" / "images"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "yolo_detections.csv"

MODEL_NAME = "yolov8n.pt"


def categorize_image(detected_classes):
    classes = set(detected_classes)

    has_person = "person" in classes
    has_product = any(
        item in classes
        for item in ["bottle", "cup", "vase", "box", "cell phone", "book"]
    )

    if has_person and has_product:
        return "promotional"
    elif has_product and not has_person:
        return "product_display"
    elif has_person and not has_product:
        return "lifestyle"
    else:
        return "other"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model = YOLO(MODEL_NAME)
    image_files = list(IMAGE_DIR.rglob("*.jpg")) + list(IMAGE_DIR.rglob("*.png"))

    if not image_files:
        raise FileNotFoundError("No images found in data/raw/images")

    results_list = []

    for image_path in image_files:
        channel_name = image_path.parent.name
        message_id = image_path.stem

        results = model(str(image_path), verbose=False)

        detected_classes = []
        confidences = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]

                detected_classes.append(class_name)
                confidences.append(confidence)

        image_category = categorize_image(detected_classes)

        if detected_classes:
            for detected_class, confidence in zip(detected_classes, confidences):
                results_list.append({
                    "message_id": message_id,
                    "channel_name": channel_name,
                    "image_path": str(image_path),
                    "detected_class": detected_class,
                    "confidence_score": confidence,
                    "image_category": image_category
                })
        else:
            results_list.append({
                "message_id": message_id,
                "channel_name": channel_name,
                "image_path": str(image_path),
                "detected_class": "none",
                "confidence_score": 0.0,
                "image_category": "other"
            })

    df = pd.DataFrame(results_list)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Processed images: {len(image_files)}")
    print(f"Detection rows saved: {len(df)}")
    print(f"Output file: {OUTPUT_FILE}")
    print("\nImage category summary:")
    print(df["image_category"].value_counts())


if __name__ == "__main__":
    main()