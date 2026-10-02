# from ultralytics import YOLO

# model = YOLO("yolo26n.pt")

# results = model.predict(
#     source="videos/test.mp4",
#     conf=0.40,
#     save=True
# )

# print("Video detection completed!")




from ultralytics import YOLO


# --------------------------------------------------
# PATHS
# --------------------------------------------------

MODEL_PATH = r"runs\rakshakai_train\weights\best.pt"

VIDEO_PATH = r"videos\test.mp4"


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

model = YOLO(MODEL_PATH)


# --------------------------------------------------
# RUN VIDEO DETECTION
# --------------------------------------------------

results = model.predict(
    source=VIDEO_PATH,
    imgsz=640,
    conf=0.40,
    device=0,
    save=True,
    project=r"D:\RakshakAI\runs",
    name="rakshakai_video",
    exist_ok=True
)


# --------------------------------------------------
# COMPLETED
# --------------------------------------------------

print("\n" + "=" * 60)
print("VIDEO DETECTION COMPLETED")
print("=" * 60)

print("\nModel:")
print(MODEL_PATH)

print("\nInput video:")
print(VIDEO_PATH)

print("\nOutput saved inside:")
print(r"D:\RakshakAI\runs\rakshakai_video")