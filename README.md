\# RAKSHAK AI

\### AI-Based Restricted Zone \& Safety Monitoring System



RAKSHAK AI is an AI-based video monitoring system designed to detect and monitor people and vehicles in defined restricted/safe zones.



The system combines object detection, object tracking, virtual-zone monitoring, event detection, event prioritization, event storage, and a web dashboard into a single monitoring workflow.



\---



\## 1. System Workflow



```text

Camera / Video

&#x20;     ↓

YOLO Object Detection

&#x20;     ↓

ByteTrack Object Tracking

&#x20;     ↓

Virtual Zone Monitoring

&#x20;     ↓

Zone Violation Detection

&#x20;     ↓

Event Detection \& Priority

&#x20;     ↓

Timestamp + Event Details

&#x20;     ↓

CSV Event Storage

&#x20;     ↓

FastAPI Backend

&#x20;     ↓

Web Dashboard

```



\---



\## 2. Key Features



\### AI Detection

\- Detects objects such as people and vehicles from video.

\- Uses YOLO for object detection.

\- Assigns tracking IDs using ByteTrack.



\### Restricted Zone Monitoring

\- Uses virtual zones to define monitored areas.

\- Tracks object movement relative to the defined zone.

\- Detects zone-related events.



\### Event Engine



The system supports the following event types:



\- `ENTER`

\- `LOITERING`

\- `EXIT`

\- `REPEATED\_VIOLATION`



Events contain information such as:



\- Timestamp

\- Event type

\- Object type

\- Track ID

\- Zone name

\- Duration

\- Detection confidence



\### Event Storage



Events are recorded in:



```text

outputs/events.csv

```



The event history can therefore be used by the dashboard for monitoring and searching previously generated events.



\---



\# 3. Web Dashboard



The dashboard provides a user interface for monitoring the RAKSHAK AI system.



\### Dashboard / Overview



Provides a high-level view of the system, including:



\- Total events

\- Event statistics

\- Recent detection events

\- System health/status

\- Monitoring information



\### Live Monitoring



Displays the processed video stream through the web dashboard.



The dashboard connects to the FastAPI backend to receive the live video feed.



\### Alerts



Displays important events and provides a quick way to identify events requiring attention.



Events are presented according to their detected event/severity information.



\### Detection Events



Provides access to the stored event history.



Users can:



\- Search events

\- Filter events by type

\- Search events by date

\- Select an event to view its details



The event detail view includes information such as:



\- Timestamp

\- Event type

\- Object type

\- Track ID

\- Zone

\- Duration

\- Confidence



\### Analytics



Provides graphical summaries of the available detection/event data.



\### Settings



Provides dashboard-level settings such as:



\- Dark/light theme

\- Auto-refresh

\- System information



\---



\# 4. Backend API



The dashboard uses a FastAPI backend.



Main endpoints include:



```text

GET /api/health

GET /api/events

GET /api/stats

GET /api/video

```



\### Health



```text

GET /api/health

```



Returns the current API/system status and checks whether required event/stream files are available.



\### Events



```text

GET /api/events

```



Returns stored events.



Optional parameters include:



```text

limit

date

```



Example:



```text

/api/events?limit=100\&date=2026-11-12

```



\### Statistics



```text

GET /api/stats

```



Returns event counts for different event categories.



\### Video



```text

GET /api/video

```



Provides the processed video stream to the dashboard.



\---



\# 5. Technology Stack



\## AI / Computer Vision



\- Python

\- YOLO

\- ByteTrack

\- OpenCV



\## Backend



\- FastAPI

\- Uvicorn

\- Python



\## Frontend



\- React

\- Vite

\- JavaScript

\- CSS

\- Lucide React

\- Recharts



\## Storage



\- CSV-based event storage



\## Development



\- Git

\- GitHub

\- VS Code



\---



\# 6. Project Structure



```text

RAKSHAK-AI/

│

├── src/

│   ├── event\_monitor.py

│   ├── event\_engine.py

│   ├── zone\_monitor.py

│   ├── zone\_utils.py

│   └── ...

│

├── backend/

│   └── main.py

│

├── frontend/

│   ├── src/

│   │   ├── App.jsx

│   │   ├── App.css

│   │   └── main.jsx

│   ├── public/

│   ├── package.json

│   └── vite.config.js

│

├── outputs/

│   └── events.csv

│

├── stream/

│

├── weights/

│

├── .gitignore

└── README.md

```



Generated runtime folders such as `outputs/` and `stream/` are intended for local runtime data and are excluded from Git tracking.



\---



\# 7. Running the Backend



From the project root:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



Then:



```powershell

python -m uvicorn backend.main:app --reload --port 8000

```



The backend runs at:



```text

http://127.0.0.1:8000

```



API health check:



```text

http://127.0.0.1:8000/api/health

```



\---



\# 8. Running the Frontend



Open another terminal and navigate to the frontend:



```powershell

cd frontend

```



Install dependencies if required:



```powershell

npm install

```



Start the development server:



```powershell

npm run dev

```



The Vite development server normally runs at:



```text

http://localhost:5173

```



The frontend communicates with the FastAPI backend running on port `8000`.



\---



\# 9. Dashboard Data Flow



```text

RAKSHAK Detection/Event System

&#x20;           ↓

&#x20;      events.csv

&#x20;           ↓

&#x20;      FastAPI API

&#x20;           ↓

&#x20;       React App

&#x20;           ↓

&#x20;     Web Dashboard

```



For live monitoring:



```text

Processed Video Frame

&#x20;       ↓

&#x20;  Stream Frame

&#x20;       ↓

&#x20;    FastAPI

&#x20;       ↓

&#x20;  React Dashboard

&#x20;       ↓

&#x20;  Live Monitoring

```



\---



\# 10. Dashboard Contribution



The dashboard/frontend work adds a web-based interface on top of the existing RAKSHAK AI detection and event-monitoring pipeline.



The dashboard contribution includes:



\- React-based monitoring interface

\- Professional security-monitoring UI

\- Dashboard overview

\- Live monitoring page

\- Alerts page

\- Detection event history

\- Date-based event search

\- Event filtering

\- Event detail modal

\- Analytics visualizations

\- Settings page

\- Dark/light theme

\- Auto-refresh

\- System health display

\- FastAPI integration

\- Live video stream integration



The existing detection, tracking, restricted-zone and event-engine components remain part of the overall RAKSHAK AI system.



\---



\# 11. Development Branch



Dashboard development is maintained separately from the existing project branches.



Current dashboard branch:



```text

dashboard-frontend

```



Changes from this branch can be reviewed through a Pull Request before merging into the target project branch.



\---



\# 12. Project Objective



RAKSHAK AI aims to provide an automated monitoring solution for restricted or safety-sensitive areas by combining computer vision, object tracking, zone-based event detection, and a centralized monitoring dashboard.



The system is designed to make detected events easier to monitor, review, and analyze through a web-based interface.

