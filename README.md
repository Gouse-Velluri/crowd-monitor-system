# 🧠 Smart Crowd Density Monitor

A production-ready Django project with real-time WebSocket updates, AI person detection (YOLO/Haar), REST API, live heatmap dashboard, and an alert system.
Smart Crowd Density Monitor is a real-time AI system that:

• Detects people using YOLO
• Calculates occupancy percentage
• Broadcasts updates instantly using WebSockets
• Triggers automated safety alerts
• Stores historical analytics
• Deploys to cloud using ASGI architecture

It demonstrates production-level backend engineering with real-time architecture and AI integration.

🌍 Problem Statement

High-density public spaces like:

Railway stations

Stadiums

Malls

Religious gatherings

Political rallies

are vulnerable to:

Stampedes

Overcrowding

Emergency delays

Safety violations

Manual monitoring is reactive and unreliable.

A scalable automated monitoring system is required.

💡 Solution Overview

Smart Crowd Density Monitor provides:

✔ AI person detection
✔ Real-time occupancy tracking
✔ Density classification
✔ Automated alert triggering
✔ Live dashboard updates
✔ Historical crowd analytics
✔ Heatmap visualization
✔ Cloud-ready deployment

It functions like a mini smart-city control backend.

---

## 🏗 Project Structure

```
crowd_monitor/
├── crowd_monitor/          # Project core
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py             # WebSocket entry point
│   └── routing.py          # WebSocket URL routes
├── locations/              # Location & crowd count models
│   ├── models.py           # Location, CrowdLog
│   ├── views.py            # REST API + WebSocket broadcast
│   ├── consumers.py        # WebSocket consumers
│   ├── serializers.py
│   └── fixtures/           # Sample data
├── detection/              # AI detection engine
│   ├── detector.py         # HaarDetector + YOLODetector
│   ├── views.py            # REST endpoints for detection
│   └── management/
│       └── commands/
│           └── run_detection.py   # Background polling command
├── alerts/                 # Alert system
│   ├── models.py
│   ├── utils.py            # check_and_trigger_alerts()
│   └── views.py
├── dashboard/              # HTML frontend
│   └── views.py
├── templates/
│   └── dashboard/
│       ├── base.html
│       ├── index.html            # Live map + cards + chart
│       ├── location_detail.html  # Single location view
│       └── alerts.html
├── requirements.txt
└── manage.py
```

---

## ⚡ Quick Start

### 1. Install dependencies

```bash
pip install django djangorestframework "channels[daphne]" channels-redis django-cors-headers
```

For AI detection (optional):
```bash
pip install opencv-python ultralytics   # YOLO
```

### 2. Start Redis (for WebSocket channel layer)

```bash
docker run -p 6379:6379 redis:alpine
```

> **No Redis?** Edit `settings.py` and switch to InMemoryChannelLayer (see comments).

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Load sample data

```bash
python manage.py loaddata locations/fixtures/sample_locations.json
```

### 5. Create admin user

```bash
python manage.py createsuperuser
```

### 6. Start the server (ASGI)

```bash
daphne -p 8000 crowd_monitor.asgi:application
# or
python manage.py runserver   # WebSockets also work in dev
```

### 7. (Optional) Run AI detection

```bash
python manage.py run_detection --mode yolo --interval 5
```

---

## 🌐 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Live dashboard (map + cards + chart) |
| `/location/<id>/` | Single location detail |
| `/alerts/` | Alert log |
| `/admin/` | Django admin |
| `ws://localhost:8000/ws/crowd/` | All-locations WebSocket |
| `ws://localhost:8000/ws/crowd/<id>/` | Single-location WebSocket |

---

## 📡 REST API

### Locations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/locations/` | List all locations |
| POST | `/api/locations/` | Create location |
| GET | `/api/locations/<id>/` | Location detail |
| POST | `/api/locations/<id>/update-count/` | Update crowd count |
| GET | `/api/locations/<id>/logs/` | Count history |
| GET | `/api/locations/<id>/stats/` | 24h statistics |

**Example — update count (manual or from script):**
```bash
curl -X POST http://localhost:8000/api/locations/1/update-count/ \
     -H "Content-Type: application/json" \
     -d '{"count": 85, "source": "MANUAL"}'
```

### Detection

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/detection/detect/` | Detect from base64 image |
| POST | `/api/detection/detect/<id>/` | Detect from camera & update location |

### Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts/` | List alerts |
| GET | `/api/alerts/?status=ACTIVE` | Active alerts only |
| POST | `/api/alerts/<id>/resolve/` | Resolve an alert |

---

## 🧠 AI Detection Engine

### `detection/detector.py`

Two classes:

**`HaarDetector`** — Uses OpenCV HOG descriptor. Fast, no GPU needed.

**`YOLODetector`** — Uses YOLOv8 (ultralytics). More accurate.

```python
from detection.detector import get_detector

detector = get_detector('yolo')   # or 'haar'

# From webcam
count = detector.detect_from_camera(source=0, duration_seconds=5)

# From RTSP stream
count = detector.detect_from_camera(source='rtsp://192.168.1.10:554/stream')

# From single frame (numpy array)
count = detector.detect_from_frame(frame)
```

### Run continuous detection

```bash
python manage.py run_detection --mode yolo --interval 5
# Only one location:
python manage.py run_detection --location 1 --mode haar
```

---

## 🔌 WebSocket Protocol

**Connect:** `ws://localhost:8000/ws/crowd/`

**On connect**, server sends:
```json
{ "type": "initial_state", "data": [ ...all locations... ] }
```

**On every count update**, server broadcasts:
```json
{
  "type": "crowd_update",
  "data": {
    "location_id": 1,
    "location_name": "Main Library",
    "current_count": 85,
    "capacity_limit": 300,
    "density_level": "MEDIUM",
    "occupancy_percentage": 28.3,
    "last_updated": "2025-01-01T12:00:00Z"
  }
}
```

---

## 🚨 Alert System

Alerts trigger automatically when:
- Crowd exceeds **80% capacity** → `OVERCROWD` alert
- Count jumps **>30%** between readings → `SPIKE` alert

Notifications are sent via email (configure `settings.py`):
```python
ALERT_EMAIL_FROM = 'alerts@crowdmonitor.com'
ALERT_EMAIL_TO   = ['admin@example.com']
```

---

## 🚀 Production Deployment

```bash
# 1. Switch to PostgreSQL in settings.py
# 2. Set DEBUG=False, update ALLOWED_HOSTS
# 3. Collect static files
python manage.py collectstatic

# 4. Use gunicorn + daphne behind nginx
daphne -b 0.0.0.0 -p 8000 crowd_monitor.asgi:application

# 5. Run Redis
docker run -d -p 6379:6379 redis:alpine
```

---

## 🔮 Extension Ideas

- **Predictive Analysis** — Use scikit-learn on `CrowdLog` to forecast peak hours
- **Anomaly Detection** — Z-score or moving average on crowd counts
- **SMS Alerts** — Integrate Twilio in `alerts/utils.py`
- **Custom YOLO model** — Train on your own camera footage for better accuracy
- **Mobile PWA** — The dashboard is mobile-responsive; add a service worker

---

## 🛠 Tech Stack

| Layer         | Technology                |
| ------------- | ------------------------- |
| Backend       | Django 4.x                |
| API           | Django REST Framework     |
| Real-Time     | Django Channels           |
| Channel Layer | Redis                     |
| ASGI Server   | Gunicorn + Uvicorn Worker |
| AI            | OpenCV + YOLOv8           |
| Database      | PostgreSQL                |
| Frontend      | HTML + Tailwind CSS       |
| Visualization | Chart.js                  |
| Heatmaps      | Leaflet.js                |
| Deployment    | Render                    |

