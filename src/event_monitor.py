import csv
import os
import time
from datetime import datetime

import cv2
from ultralytics import YOLO

from event_engine import EventEngine
from zone_utils import (
    SAFE,
    build_zones,
    find_zone,
    get_foot_point,
    new_track_state,
    update_zone_state,
)


# ---------------- SETTINGS ----------------

# Project root = the folder that contains src, weights, outputs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "weights", "yolo26n.pt")

# Video source: webcam is the default.
# To test on a video, put # in front of the webcam line and
# remove the # from the video line.
SOURCE = 0
# SOURCE = os.path.join(BASE_DIR, "videos", "test.mp4")

# None = default tracker (same as track_test.py)
TRACKER_CONFIG = None

# Frames an object must stay in the new zone before the change is confirmed
CONFIRM_FRAMES = 5

# A lost track is cleaned up after this many missing frames
MAX_MISSING_FRAMES = 30

# Seconds in a restricted zone before a LOITERING event fires.
# 5 is good for testing. Use a larger value (e.g. 30) for real use.
DWELL_SECONDS = 5

# REPEATED_VIOLATION: this many entries by the same track ...
REPEAT_LIMIT = 3
# ... within this many seconds
REPEAT_WINDOW_SECONDS = 60

# How long the ALERT banner stays on screen (in frames)
ALERT_FRAMES = 40

CSV_PATH = os.path.join(BASE_DIR, "outputs", "events.csv")
CSV_HEADER = [
    "timestamp", "event_type", "object_type", "track_id",
    "zone_name", "duration_sec", "confidence",
]

# Only the restricted zone is defined. Everything outside it is Safe.
# Points are fractions of the frame (x, y), each between 0 and 1.
ZONE_CONFIG = [
    {
        "name": "Restricted Zone",
        "restricted": True,
        "points": [(0.55, 0.25), (0.95, 0.25), (0.95, 1.0), (0.55, 1.0)],
    },
]

VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck"}

FONT = cv2.FONT_HERSHEY_SIMPLEX

COLOR_RESTRICTED = (0, 0, 255)          # red box
COLOR_SAFE = (0, 255, 0)                # green box
COLOR_ZONE = (0, 165, 255)              # orange zone


# ---------------- HELPERS ----------------

def open_csv(path):
    """Open the CSV for appending. If an old file has different columns,
    it is renamed (not deleted) and a fresh file is started."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "r", newline="", encoding="utf-8") as f:
            first_row = next(csv.reader(f), [])
        if first_row != CSV_HEADER:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = path.replace(".csv", f"_old_{stamp}.csv")
            os.replace(path, backup)
            print(f"Old CSV format found. Renamed to: {backup}")

    is_new = (not os.path.exists(path)) or os.path.getsize(path) == 0
    file = open(path, "a", newline="", encoding="utf-8")
    writer = csv.writer(file)
    if is_new:
        writer.writerow(CSV_HEADER)
        file.flush()
    return file, writer


def log_event(file, writer, event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow([
        timestamp,
        event["event_type"],
        event["object_type"],
        event["track_id"],
        event["zone_name"],
        f"{event['duration']:.1f}",
        f"{event['confidence']:.2f}",
    ])
    file.flush()

    if event["event_type"] == "REPEATED_VIOLATION":
        detail = (
            f"{event['count']} entries within {event['duration']:.1f}s, "
            f"conf {event['confidence']:.2f}"
        )
    else:
        detail = (
            f"stay {event['duration']:.1f}s, "
            f"conf {event['confidence']:.2f}"
        )

    print(
        f"[{timestamp}] {event['event_type']}: "
        f"{event['object_type']} #{event['track_id']} "
        f"{event['zone_name']} ({detail})"
    )


def banner_text_for(event):
    """Return the on-screen alert text for an event, or None."""
    who = f"{event['object_type']} #{event['track_id']}"
    if event["event_type"] == "ENTER":
        return f"ALERT: Restricted Zone Entry ({who})"
    if event["event_type"] == "LOITERING":
        return f"ALERT: Loitering ({who}, {int(event['duration'])}s)"
    if event["event_type"] == "REPEATED_VIOLATION":
        return f"ALERT: Repeated Violation ({who}, {event['count']} entries)"
    return None


def zone_label(zone_name):
    """Short label for the video: 'Restricted Zone' -> 'Restricted'."""
    return zone_name.replace(" Zone", "")


def draw_zones(frame, zones):
    overlay = frame.copy()
    for z in zones:
        cv2.fillPoly(overlay, [z["polygon"]], COLOR_ZONE)
    cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)

    for z in zones:
        cv2.polylines(frame, [z["polygon"]], True, COLOR_ZONE, 2)
        x, y = z["polygon"][0]
        cv2.putText(
            frame, z["name"], (int(x) + 5, int(y) + 22),
            FONT, 0.6, COLOR_ZONE, 2
        )


def draw_alert(frame, text):
    frame_w = frame.shape[1]
    cv2.rectangle(frame, (0, 0), (frame_w, 45), (0, 0, 255), -1)
    cv2.putText(frame, text, (15, 31), FONT, 0.8, (255, 255, 255), 2)


# ---------------- MAIN ----------------

def main():
    is_webcam = isinstance(SOURCE, int)

    if not is_webcam and not os.path.exists(SOURCE):
        print(f"Error: video file not found: {SOURCE}")
        return

    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(SOURCE)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    if is_webcam:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    window_name = "RakshakAI - Event Engine"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    csv_file, csv_writer = open_csv(CSV_PATH)

    track_kwargs = {"persist": True, "imgsz": 960, "verbose": False}
    if TRACKER_CONFIG:
        track_kwargs["tracker"] = TRACKER_CONFIG

    # track_id -> zone confirmation state (Phase 3 logic)
    track_states = {}
    zones = None
    engine = None
    restricted_names = set()

    frame_no = 0
    alert_until = 0
    alert_text = ""

    print("Event engine started.")
    print(f"Loitering fires after {DWELL_SECONDS}s inside a restricted zone.")
    print(
        f"Repeated violation fires after {REPEAT_LIMIT} entries "
        f"within {REPEAT_WINDOW_SECONDS}s."
    )
    print("To stop: click the video window and press Q or Esc, "
          "or close the window.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video ended or frame could not be read.")
            break

        if is_webcam:
            frame = cv2.flip(frame, 1)
            now = time.time()
        else:
            # Use the video's own clock so the stay time is correct
            # even when processing is slower than real time.
            now = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        frame_no += 1
        frame_h, frame_w = frame.shape[:2]

        if zones is None:
            zones = build_zones(ZONE_CONFIG, frame.shape)
            restricted_names = {z["name"] for z in zones if z["restricted"]}
            engine = EventEngine(
                list(restricted_names),
                DWELL_SECONDS,
                REPEAT_LIMIT,
                REPEAT_WINDOW_SECONDS,
            )

        results = model.track(frame, **track_kwargs)
        result = results[0]

        draw_zones(frame, zones)

        seen_ids = set()

        if result.boxes is not None:
            boxes = result.boxes
            track_ids = boxes.id

            for i, box in enumerate(boxes):
                class_name = model.names[int(box.cls[0])]
                confidence = float(box.conf[0])

                if class_name == "person":
                    object_type = "Person"
                elif class_name in VEHICLE_CLASSES:
                    object_type = "Vehicle"
                else:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                track_id = int(track_ids[i]) if track_ids is not None else -1

                foot_point = get_foot_point(x1, y1, x2, y2, frame_w, frame_h)
                raw_zone = find_zone(foot_point, zones)

                dwell = 0.0

                if track_id != -1:
                    seen_ids.add(track_id)

                    state = track_states.get(track_id)
                    if state is None:
                        state = new_track_state(object_type, confidence)
                        track_states[track_id] = state

                    state["missing"] = 0
                    state["type"] = object_type
                    state["conf"] = confidence

                    # Phase 3: confirm the zone (boundary stability)
                    update_zone_state(state, raw_zone, CONFIRM_FRAMES)
                    current_zone = state["zone"]

                    # Phase 4: feed the confirmed zone to the event engine
                    new_events = engine.update(
                        track_id, object_type, current_zone, confidence, now
                    )
                    for event in new_events:
                        log_event(csv_file, csv_writer, event)
                        text = banner_text_for(event)
                        if text:
                            alert_text = text
                            alert_until = frame_no + ALERT_FRAMES

                    dwell = engine.get_dwell(track_id, now)
                else:
                    # Not tracked yet: show the raw zone, no events
                    current_zone = raw_zone

                # Drawing
                if current_zone in restricted_names:
                    color = COLOR_RESTRICTED
                    text_color = (255, 255, 255)
                else:
                    color = COLOR_SAFE
                    text_color = (0, 0, 0)

                parts = []
                if track_id != -1:
                    parts.append(f"{object_type} #{track_id}")
                else:
                    parts.append(object_type)
                parts.append(zone_label(current_zone))
                if dwell > 0:
                    parts.append(f"{int(dwell)}s")
                parts.append(f"{confidence:.2f}")
                label = " | ".join(parts)

                (text_w, _), _ = cv2.getTextSize(label, FONT, 0.6, 2)
                top = max(y1 - 30, 0)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.rectangle(
                    frame, (x1, top), (x1 + text_w + 10, top + 30), color, -1
                )
                cv2.putText(
                    frame, label, (x1 + 5, top + 21),
                    FONT, 0.6, text_color, 2
                )
                cv2.circle(frame, foot_point, 5, (255, 0, 0), -1)

        # Clean up tracks that disappeared (temporary loss is safe)
        for track_id in list(track_states.keys()):
            if track_id in seen_ids:
                continue

            state = track_states[track_id]
            state["missing"] += 1

            if state["missing"] > MAX_MISSING_FRAMES:
                for event in engine.remove_track(track_id, now):
                    log_event(csv_file, csv_writer, event)
                del track_states[track_id]

        if frame_no <= alert_until:
            draw_alert(frame, alert_text)

        cv2.imshow(window_name, frame)

        # Stop keys: q, Q (Caps Lock safe) or Esc
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q"), 27):
            break

        # Stop when the window is closed with the X button
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    csv_file.close()
    cv2.destroyAllWindows()
    print("Event engine stopped.")


if __name__ == "__main__":
    main()