
from pathlib import Path
import csv
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


BASE_DIR = Path(__file__).resolve().parent.parent

EVENTS_FILE = BASE_DIR / "outputs" / "events.csv"
STREAM_FRAME = BASE_DIR / "stream" / "latest.jpg"


app = FastAPI(
    title="RakshakAI API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "project": "RakshakAI",
        "events_file_exists": EVENTS_FILE.exists(),
        "stream_frame_exists": STREAM_FRAME.exists(),
    }


@app.get("/api/events")
def get_events(limit: int = 100):
    limit = max(1, min(limit, 1000))

    if not EVENTS_FILE.exists():
        return {
            "count": 0,
            "events": [],
        }

    with EVENTS_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        events = list(csv.DictReader(file))
    
    events = events[-limit:]
    events.reverse()

    return {
        "count": len(events),
        "events": events,
    }


@app.get("/api/stats")
def get_stats():
    if not EVENTS_FILE.exists():
        return {
            "total_events": 0,
            "enter_events": 0,
            "exit_events": 0,
            "loitering_events": 0,
            "repeated_violations": 0,
        }

    with EVENTS_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        events = list(csv.DictReader(file))

    event_types = [
        event.get("event_type", "").upper()
        for event in events
    ]

    return {
        "total_events": len(events),
        "enter_events": event_types.count("ENTER"),
        "exit_events": event_types.count("EXIT"),
        "loitering_events": event_types.count("LOITERING"),
        "repeated_violations": event_types.count(
            "REPEATED_VIOLATION"
        ),
    }


def generate_video_stream():
    """
    Continuously send the latest processed camera frame
    as an MJPEG stream.
    """

    last_frame = None

    while True:
        if STREAM_FRAME.exists():
            try:
                frame_bytes = STREAM_FRAME.read_bytes()

                # Only send when a new/different frame is available.
                if frame_bytes != last_frame:
                    last_frame = frame_bytes

                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + frame_bytes
                        + b"\r\n"
                    )

            except OSError:
                # File may be temporarily being rewritten.
                pass

        time.sleep(0.05)


@app.get("/api/video")
def video_feed():
    return StreamingResponse(
        generate_video_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
