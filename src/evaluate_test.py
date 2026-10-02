from ultralytics import YOLO


# --------------------------------------------------
# LOAD TRAINED MODEL
# --------------------------------------------------

model = YOLO(
    r"runs\rakshakai_train\weights\best.pt"
)


# --------------------------------------------------
# EVALUATE ON TEST DATASET
# --------------------------------------------------

results = model.val(
    data="dataset/data.yaml",
    split="test",
    imgsz=640,
    batch=8,
    device=0,
    workers=0,
    project=r"D:\RakshakAI\runs",
    name="rakshakai_test",
    exist_ok=True
)


# --------------------------------------------------
# PRINT RESULTS
# --------------------------------------------------

print("\n" + "=" * 60)
print("TEST DATASET EVALUATION COMPLETED")
print("=" * 60)

print("\nBest model:")
print(
    r"runs\rakshakai_train\weights\best.pt"
)

print("\nTest results saved at:")
print(
    r"D:\RakshakAI\runs\rakshakai_test"
)