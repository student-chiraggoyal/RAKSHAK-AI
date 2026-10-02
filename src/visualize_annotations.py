from pathlib import Path
import cv2

# Original images
image_folder = Path("dataset/raw")

# Generated YOLO labels
label_folder = Path("dataset/raw_labels")

# Output folder
output_folder = Path("outputs/annotation_check")
output_folder.mkdir(parents=True, exist_ok=True)

# Our classes
class_names = {
    0: "person",
    1: "vehicle"
}

image_extensions = {".jpg", ".jpeg", ".png"}

for image_path in image_folder.iterdir():

    if image_path.suffix.lower() not in image_extensions:
        continue

    label_path = label_folder / f"{image_path.stem}.txt"

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not read: {image_path.name}")
        continue

    height, width = image.shape[:2]

    if label_path.exists():

        with open(label_path, "r") as f:
            lines = f.readlines()

        for line in lines:

            parts = line.strip().split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])

            x_center = float(parts[1])
            y_center = float(parts[2])
            box_width = float(parts[3])
            box_height = float(parts[4])

            # Convert normalized coordinates to pixels
            x_center *= width
            y_center *= height
            box_width *= width
            box_height *= height

            x1 = int(x_center - box_width / 2)
            y1 = int(y_center - box_height / 2)
            x2 = int(x_center + box_width / 2)
            y2 = int(y_center + box_height / 2)

            # Keep coordinates inside image
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(width - 1, x2)
            y2 = min(height - 1, y2)

            label = class_names.get(class_id, "unknown")

            # Draw bounding box
            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # Draw class name
            cv2.putText(
                image,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    output_path = output_folder / image_path.name

    cv2.imwrite(str(output_path), image)

    print(f"Saved: {output_path}")

print("\nAnnotation visualization completed!")
print(f"Check images in: {output_folder}")