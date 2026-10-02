# import cv2
# from ultralytics import YOLO


# # Load YOLO model
# model = YOLO("weights/yolo26n.pt")

# # Open webcam
# cap = cv2.VideoCapture(0)

# if not cap.isOpened():
#     print("Error: Could not open webcam.")
#     exit()

# # Set webcam resolution
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# # Create normal resizable window
# window_name = "RakshakAI - Object Tracking"

# cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# # Set initial window size
# cv2.resizeWindow(window_name, 1280, 720)

# print("Tracking started.")
# print("Press Q to stop.")

# while True:

#     # Read frame
#     ret, frame = cap.read()

#     if not ret:
#         print("Error: Could not read frame.")
#         break

#     # Mirror webcam preview
#     frame = cv2.flip(frame, 1)

#     # Run YOLO tracking
#     results = model.track(
#         frame,
#         persist=True,
#         verbose=False
#     )

#     # Draw tracking results
#     annotated_frame = results[0].plot()

#     # Show frame
#     cv2.imshow(window_name, annotated_frame)

#     # Press Q to stop
#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break


# # Release resources
# cap.release()
# cv2.destroyAllWindows()

# print("Tracking stopped.")










import cv2
from ultralytics import YOLO


# Load YOLO model
model = YOLO("weights/yolo26n.pt")
# model = YOLO("runs/rakshakai_train/weights/best.pt")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Webcam resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Window
window_name = "RakshakAI - Object Tracking"

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1280, 720)


# Classes we want to track
vehicle_classes = {
    "car",
    "motorcycle",
    "bus",
    "truck"
}

print("Tracking started.")
print("Press Q to stop.")


while True:

    # Read frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    # Mirror webcam
    frame = cv2.flip(frame, 1)

    # Run tracking
    # results = model.track(
    #     frame,
    #     persist=True,
    #     verbose=False
    # )
    results = model.track(
        frame,
        persist=True,
        # tracker="botsort.yaml",
        # tracker="trackers/bytetrack_rakshakai.yaml",
        # tracker="trackers/ocsort_rakshakai.yaml",
        imgsz=960,
        verbose=False
    )

    result = results[0]

    # Draw our own tracking information
    if result.boxes is not None:

        boxes = result.boxes

        # Get tracking IDs
        track_ids = boxes.id

        for i, box in enumerate(boxes):

            # Class ID
            class_id = int(box.cls[0])

            # Class name
            class_name = model.names[class_id]

            # Confidence
            confidence = float(box.conf[0])

            # Track ID
            if track_ids is not None:
                track_id = int(track_ids[i])
            else:
                track_id = -1

            # Keep only Person and Vehicle
            if class_name == "person":

                object_type = "Person"

            elif class_name in vehicle_classes:

                object_type = "Vehicle"

            else:

                continue

            # Bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Label
            if track_id != -1:

                label = (
                    f"{object_type} #{track_id} "
                    f"{confidence:.2f}"
                )

            else:

                label = (
                    f"{object_type} "
                    f"{confidence:.2f}"
                )

            # Draw bounding box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # Draw label background
            cv2.rectangle(
                frame,
                (x1, y1 - 30),
                (x2, y1),
                (0, 255, 0),
                -1
            )

            # Draw label
            cv2.putText(
                frame,
                label,
                (x1 + 5, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )

    # Show frame
    cv2.imshow(window_name, frame)

    # Q = quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Cleanup
cap.release()
cv2.destroyAllWindows()

print("Tracking stopped.")