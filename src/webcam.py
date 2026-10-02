# from ultralytics import YOLO

# model = YOLO("yolo26n.pt")

# model.predict(
#     source=0,
#     conf=0.40,
#     show=True
# )






import cv2
from ultralytics import YOLO


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

MODEL_PATH = r"runs\rakshakai_train\weights\best.pt"

model = YOLO(MODEL_PATH)


# --------------------------------------------------
# OPEN WEBCAM
# --------------------------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    exit()


# Camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# --------------------------------------------------
# CREATE WINDOW
# --------------------------------------------------

WINDOW_NAME = "RakshakAI - Live Detection"

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    WINDOW_NAME,
    1280,
    720
)


print("=" * 60)
print("RAKSHAKAI LIVE DETECTION")
print("=" * 60)
print("Press Q or ESC to stop.")
print("You can also close the camera window.")


# --------------------------------------------------
# LIVE DETECTION
# --------------------------------------------------

while True:

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read frame.")
        break

    frame = cv2.flip(frame, 1)

    # --------------------------------------------------
    # YOLO DETECTION
    # --------------------------------------------------

    results = model.predict(
        source=frame,
        imgsz=640,
        conf=0.40,
        device=0,
        verbose=False
    )


    # --------------------------------------------------
    # DRAW DETECTIONS
    # --------------------------------------------------

    annotated_frame = results[0].plot()


    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    cv2.imshow(
        WINDOW_NAME,
        annotated_frame
    )


    # --------------------------------------------------
    # KEYBOARD CONTROL
    # --------------------------------------------------

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or key == ord("Q"):
        break

    if key == 27:  # ESC
        break


# --------------------------------------------------
# CLEANUP
# --------------------------------------------------

cap.release()

cv2.destroyAllWindows()

print("\nWebcam detection stopped.")