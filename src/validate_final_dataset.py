from pathlib import Path


DATASET = Path("dataset")

splits = ["train", "val", "test"]

valid_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

errors = 0

total_images = 0
total_labels = 0


print("=" * 60)
print("FINAL DATASET VALIDATION")
print("=" * 60)


for split in splits:

    image_folder = DATASET / "images" / split
    label_folder = DATASET / "labels" / split

    images = [
        p for p in image_folder.iterdir()
        if p.is_file() and p.suffix.lower() in valid_extensions
    ]

    labels = list(label_folder.glob("*.txt"))

    print(f"\n{split.upper()}")
    print(f"Images : {len(images)}")
    print(f"Labels : {len(labels)}")

    total_images += len(images)
    total_labels += len(labels)

    # Check every image has a label
    for image in images:

        label = label_folder / f"{image.stem}.txt"

        if not label.exists():

            print(f"ERROR: Missing label -> {image.name}")
            errors += 1
            continue

        with open(label, "r") as f:
            lines = f.readlines()

        if len(lines) == 0:

            print(f"ERROR: Empty label -> {label.name}")
            errors += 1
            continue

        for line_number, line in enumerate(lines, start=1):

            parts = line.strip().split()

            if len(parts) != 5:

                print(
                    f"ERROR: Wrong format -> "
                    f"{label.name}, line {line_number}"
                )

                errors += 1
                continue

            try:

                class_id = int(parts[0])

                x = float(parts[1])
                y = float(parts[2])
                w = float(parts[3])
                h = float(parts[4])

            except ValueError:

                print(
                    f"ERROR: Invalid numbers -> "
                    f"{label.name}, line {line_number}"
                )

                errors += 1
                continue

            # Only two classes allowed
            if class_id not in [0, 1]:

                print(
                    f"ERROR: Invalid class {class_id} -> "
                    f"{label.name}"
                )

                errors += 1

            # YOLO coordinates must be 0-1
            values = [x, y, w, h]

            if not all(0 <= value <= 1 for value in values):

                print(
                    f"ERROR: Coordinates outside 0-1 -> "
                    f"{label.name}, line {line_number}"
                )

                errors += 1


print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)

print(f"Total images : {total_images}")
print(f"Total labels : {total_labels}")
print(f"Errors       : {errors}")


if errors == 0 and total_images == total_labels:

    print("\nFINAL DATASET VALIDATION PASSED!")

else:

    print("\nDATASET VALIDATION FAILED!")