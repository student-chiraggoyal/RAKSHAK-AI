from pathlib import Path
from ultralytics import YOLO

# Pretrained YOLO model
model = YOLO("yolo26n.pt")

# Input images
input_folder = Path("dataset/raw")

# Generated YOLO labels
label_folder = Path("dataset/raw_labels")
label_folder.mkdir(parents=True, exist_ok=True)

# YOLO classes that we want to convert into our 2 classes
vehicle_classes = {
    "car",
    "truck",
    "bus",
    "motorcycle"
}

# Image extensions
image_extensions = {".jpg", ".jpeg", ".png"}

images = [
    p for p in input_folder.iterdir()
    if p.suffix.lower() in image_extensions
]

print(f"Found {len(images)} images.")

for image_path in images:

    print(f"Processing: {image_path.name}")

    results = model(
        str(image_path),
        conf=0.40,
        verbose=False
    )

    label_path = label_folder / f"{image_path.stem}.txt"

    with open(label_path, "w") as f:

        for result in results:

            for box in result.boxes:

                class_id = int(box.cls[0])
                class_name = model.names[class_id]

                # Class 0 = person
                if class_name == "person":
                    new_class = 0

                # Class 1 = vehicle
                elif class_name in vehicle_classes:
                    new_class = 1

                else:
                    continue

                # YOLO normalized format:
                # x_center y_center width height
                x, y, w, h = box.xywhn[0].tolist()

                f.write(
                    f"{new_class} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n"
                )

print("\nAuto-annotation completed!")
print(f"Labels saved in: {label_folder}")