from ultralytics import YOLO
from pathlib import Path


# --------------------------------------------------
# PATHS
# --------------------------------------------------

MODEL_PATH = r"runs\rakshakai_train\weights\best.pt"
TEST_IMAGES = r"dataset\images\test"
OUTPUT_DIR = r"runs\rakshakai_test_predictions"


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

model = YOLO(MODEL_PATH)


# --------------------------------------------------
# RUN DETECTION
# --------------------------------------------------

results = model.predict(
    source=TEST_IMAGES,
    imgsz=640,
    conf=0.40,
    device=0,
    save=True,
    save_txt=True,
    save_conf=True,
    project=r"D:\RakshakAI\runs",
    name="rakshakai_test_predictions",
    exist_ok=True
)


# --------------------------------------------------
# COMPLETED
# --------------------------------------------------

print("\n" + "=" * 60)
print("TEST IMAGE DETECTION COMPLETED")
print("=" * 60)

print("\nModel:")
print(MODEL_PATH)

print("\nTest images:")
print(TEST_IMAGES)

print("\nPredictions saved at:")
print(r"D:\RakshakAI\runs\rakshakai_test_predictions")