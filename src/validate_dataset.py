from pathlib import Path

image_folder = Path("dataset/raw")
label_folder = Path("dataset/raw_labels")

valid_extensions = {".jpg", ".jpeg", ".png"}

images = [
    p for p in image_folder.iterdir()
    if p.suffix.lower() in valid_extensions
]

print(f"Images found: {len(images)}")

errors = 0

for image in images:

    label = label_folder / f"{image.stem}.txt"

    if not label.exists():
        print(f"ERROR: Label missing -> {image.name}")
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

        if class_id not in [0, 1]:
            print(
                f"ERROR: Invalid class {class_id} -> "
                f"{label.name}"
            )
            errors += 1

        values = [x, y, w, h]

        if not all(0 <= value <= 1 for value in values):
            print(
                f"ERROR: Coordinates outside 0-1 -> "
                f"{label.name}, line {line_number}"
            )
            errors += 1

if errors == 0:
    print("\nDATASET VALIDATION PASSED!")
else:
    print(f"\nValidation finished with {errors} error(s).")