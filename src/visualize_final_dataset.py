from pathlib import Path
import random
import cv2


# --------------------------------------------------
# PATHS
# --------------------------------------------------

DATASET = Path("dataset")

OUTPUT = Path("outputs/dataset_check")

OUTPUT.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

NUM_IMAGES = 20

CLASS_NAMES = {
    0: "person",
    1: "vehicle"
}


# --------------------------------------------------
# FIND IMAGES
# --------------------------------------------------

image_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


all_images = []

for split in ["train", "val", "test"]:

    image_folder = DATASET / "images" / split

    for image in image_folder.iterdir():

        if image.is_file() and image.suffix.lower() in image_extensions:

            all_images.append((split, image))


print(f"Total images available: {len(all_images)}")


# --------------------------------------------------
# RANDOM SAMPLE
# --------------------------------------------------

random.seed(42)

sample_size = min(NUM_IMAGES, len(all_images))

selected_images = random.sample(
    all_images,
    sample_size
)


# --------------------------------------------------
# PROCESS IMAGES
# --------------------------------------------------

for index, (split, image_path) in enumerate(selected_images, start=1):

    label_path = (
        DATASET
        / "labels"
        / split
        / f"{image_path.stem}.txt"
    )

    image = cv2.imread(str(image_path))

    if image is None:

        print(f"Could not read: {image_path}")
        continue


    height, width = image.shape[:2]


    # --------------------------------------------------
    # READ LABELS
    # --------------------------------------------------

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


        # --------------------------------------------------
        # YOLO → PIXEL COORDINATES
        # --------------------------------------------------

        x_center_pixel = x_center * width
        y_center_pixel = y_center * height

        box_width_pixel = box_width * width
        box_height_pixel = box_height * height


        x1 = int(
            x_center_pixel - box_width_pixel / 2
        )

        y1 = int(
            y_center_pixel - box_height_pixel / 2
        )

        x2 = int(
            x_center_pixel + box_width_pixel / 2
        )

        y2 = int(
            y_center_pixel + box_height_pixel / 2
        )


        # Keep coordinates inside image
        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width - 1))
        y2 = max(0, min(y2, height - 1))


        # --------------------------------------------------
        # CLASS NAME
        # --------------------------------------------------

        class_name = CLASS_NAMES.get(
            class_id,
            f"class_{class_id}"
        )


        # --------------------------------------------------
        # DRAW BOX
        # --------------------------------------------------

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )


        # --------------------------------------------------
        # DRAW LABEL
        # --------------------------------------------------

        cv2.putText(
            image,
            class_name,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


    # --------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------

    output_path = (
        OUTPUT
        / f"{index:02d}_{split}_{image_path.name}"
    )

    cv2.imwrite(
        str(output_path),
        image
    )


    print(f"Saved: {output_path}")


print("\nVisual annotation check completed!")
print(f"Results saved in: {OUTPUT}")