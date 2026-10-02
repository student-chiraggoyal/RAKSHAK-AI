from pathlib import Path
import shutil


# --------------------------------------------------
# PATHS
# --------------------------------------------------

SOURCE = Path(
    "kaggle_dataset/archive/Car-Person-v2-Roboflow-Owais-Ahmad"
)

DEST = Path("dataset")


# --------------------------------------------------
# DATASET SPLITS
# --------------------------------------------------

splits = {
    "train": "train",
    "valid": "val",
    "test": "test"
}


# --------------------------------------------------
# IMAGE EXTENSIONS
# --------------------------------------------------

image_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


total_images = 0
total_labels = 0
errors = 0


print("=" * 60)
print("RAKSHAKAI FINAL DATASET PREPARATION")
print("=" * 60)


# --------------------------------------------------
# PROCESS EACH SPLIT
# --------------------------------------------------

for source_split, final_split in splits.items():

    source_images = SOURCE / source_split / "images"
    source_labels = SOURCE / source_split / "labels"

    final_images = DEST / "images" / final_split
    final_labels = DEST / "labels" / final_split

    # Create destination folders
    final_images.mkdir(parents=True, exist_ok=True)
    final_labels.mkdir(parents=True, exist_ok=True)

    print(f"\nProcessing: {source_split} -> {final_split}")

    images = [
        p for p in source_images.iterdir()
        if p.is_file() and p.suffix.lower() in image_extensions
    ]

    split_images = 0
    split_labels = 0

    for image in images:

        source_image = image
        source_label = source_labels / f"{image.stem}.txt"

        destination_image = final_images / image.name
        destination_label = final_labels / f"{image.stem}.txt"

        # Check label exists
        if not source_label.exists():

            print(f"ERROR: Label missing -> {image.name}")
            errors += 1
            continue

        # Copy image
        shutil.copy2(source_image, destination_image)

        # Copy label
        shutil.copy2(source_label, destination_label)

        split_images += 1
        split_labels += 1

    total_images += split_images
    total_labels += split_labels

    print(f"Images copied : {split_images}")
    print(f"Labels copied : {split_labels}")


# --------------------------------------------------
# CREATE FINAL data.yaml
# --------------------------------------------------

data_yaml = """path: D:/RakshakAI/dataset

train: images/train
val: images/val
test: images/test

names:
  0: person
  1: vehicle
"""

yaml_path = DEST / "data.yaml"

yaml_path.write_text(data_yaml, encoding="utf-8")


# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

print("\n" + "=" * 60)
print("FINAL DATASET SUMMARY")
print("=" * 60)

print(f"Total images : {total_images}")
print(f"Total labels : {total_labels}")
print(f"Errors       : {errors}")

print("\nCreated:")
print("dataset/data.yaml")


if errors == 0 and total_images == total_labels:
    print("\nDATASET PREPARATION SUCCESSFUL!")
else:
    print("\nWARNING: Dataset preparation has errors.")