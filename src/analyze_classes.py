from pathlib import Path


DATASET = Path("dataset")

splits = ["train", "val", "test"]

class_names = {
    0: "person",
    1: "vehicle"
}

total_counts = {
    0: 0,
    1: 0
}


print("=" * 60)
print("RAKSHAKAI CLASS DISTRIBUTION")
print("=" * 60)


for split in splits:

    label_folder = DATASET / "labels" / split

    counts = {
        0: 0,
        1: 0
    }

    label_files = list(label_folder.glob("*.txt"))

    for label_file in label_files:

        with open(label_file, "r") as f:
            lines = f.readlines()

        for line in lines:

            parts = line.strip().split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])

            if class_id in counts:
                counts[class_id] += 1
                total_counts[class_id] += 1


    print(f"\n{split.upper()}")

    print(
        f"Person  : {counts[0]}"
    )

    print(
        f"Vehicle : {counts[1]}"
    )


print("\n" + "=" * 60)
print("TOTAL")
print("=" * 60)

print(
    f"Person  : {total_counts[0]}"
)

print(
    f"Vehicle : {total_counts[1]}"
)

total_objects = (
    total_counts[0] +
    total_counts[1]
)

print(
    f"Objects : {total_objects}"
)


print("\nClass distribution analysis completed!")