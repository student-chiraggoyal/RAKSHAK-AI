import cv2
import numpy as np

# Anywhere that is not inside a restricted zone counts as Safe
SAFE = "Safe"


def get_foot_point(x1, y1, x2, y2, frame_w, frame_h):
    """Bottom-center of the box, kept inside the frame."""
    center_x = (x1 + x2) // 2
    bottom_y = y2
    foot_x = min(max(center_x, 0), frame_w - 1)
    foot_y = min(max(bottom_y, 0), frame_h - 1)
    return foot_x, foot_y


def build_zones(zone_config, frame_shape):
    """Convert normalized zone points (0-1) into pixel polygons."""
    h, w = frame_shape[:2]
    zones = []
    for z in zone_config:
        pixel_points = [(int(x * w), int(y * h)) for x, y in z["points"]]
        zones.append({
            "name": z["name"],
            "restricted": z["restricted"],
            "polygon": np.array(pixel_points, dtype=np.int32),
        })
    return zones


def point_in_polygon(point, polygon):
    """True if the point is inside or on the edge of the polygon."""
    result = cv2.pointPolygonTest(
        polygon, (float(point[0]), float(point[1])), False
    )
    return result >= 0


def find_zone(point, zones):
    """Return the name of the zone the point is in.
    If it is not inside any zone, it is Safe."""
    for z in zones:
        if point_in_polygon(point, z["polygon"]):
            return z["name"]
    return SAFE


def new_track_state(object_type, confidence):
    """Every track starts as Safe and has its own independent state."""
    return {
        "zone": SAFE,
        "pending_zone": None,
        "pending": 0,
        "missing": 0,
        "type": object_type,
        "conf": confidence,
    }


def update_zone_state(state, raw_zone, confirm_frames):
    """
    Boundary confirmation (hysteresis).
    The zone only changes after raw_zone stays different for
    `confirm_frames` frames in a row.
    Returns (old_zone, new_zone) when a change is confirmed, else None.
    """
    if raw_zone == state["zone"]:
        state["pending_zone"] = None
        state["pending"] = 0
        return None

    if raw_zone == state["pending_zone"]:
        state["pending"] += 1
    else:
        state["pending_zone"] = raw_zone
        state["pending"] = 1

    if state["pending"] >= confirm_frames:
        old_zone = state["zone"]
        state["zone"] = raw_zone
        state["pending_zone"] = None
        state["pending"] = 0
        return old_zone, raw_zone

    return None