

# 🧠 Smart Crowd Density Monitor

A production-ready **real-time crowd monitoring system** built with Django, Django Channels, and AI-based person detection.

This system detects people from images or camera streams, calculates crowd density, updates dashboards instantly using WebSockets, and triggers automatic alerts when overcrowding occurs.

---

# 📌 What is This Project?

Smart Crowd Density Monitor is a scalable crowd intelligence system designed to:

* Detect number of people using AI (YOLO / OpenCV)
* Calculate occupancy percentage in real-time
* Broadcast live updates via WebSockets
* Trigger automatic safety alerts
* Store historical crowd data for analysis

It simulates a real-world smart city monitoring system.

---

# 🎯 Why Is It Useful?

Overcrowding can cause:

* Safety risks
* Stampedes
* Emergency response delays
* Security issues

This system helps authorities:

* Monitor live crowd density
* Detect abnormal spikes
* Take preventive action
* Analyze peak traffic hours
* Improve public safety planning

---

# 🏗 System Architecture

```
Camera / Image Input
        ↓
AI Detection Engine (YOLO / Haar)
        ↓
Crowd Density Calculator
        ↓
Alert Engine
        ↓
WebSocket Broadcast (Channels + Redis)
        ↓
Live Dashboard + Historical Analytics
```

---

# 🛠 Tech Stack

| Layer        | Technology              |
| ------------ | ----------------------- |
| Backend      | Django 4.x              |
| REST API     | Django REST Framework   |
| Real-Time    | Django Channels + Redis |
| ASGI Server  | Gunicorn + Uvicorn      |
| AI Detection | OpenCV + YOLOv8         |
| Database     | PostgreSQL (Production) |
| Frontend     | HTML + Tailwind CSS     |
| Charts       | Chart.js                |
| Maps         | Leaflet.js + Heatmap    |
| Deployment   | Render                  |

---

# 📂 Project Structure

```
crowd_monitor/
├── crowd_monitor/          # Core configuration
├── locations/              # Location + CrowdLog models
├── detection/              # AI detection engine
├── alerts/                 # Alert logic + trigger system
├── dashboard/              # Live frontend
├── templates/
├── requirements.txt
└── manage.py
```

---

# ⚡ Key Features

✔ AI-based person detection (YOLO / Haar)
✔ Real-time WebSocket updates
✔ Live heatmap visualization
✔ REST API endpoints
✔ Alert triggering at 80% capacity
✔ Spike detection (>30% sudden increase)
✔ Historical analytics storage
✔ Admin dashboard support
✔ Production-ready deployment setup

---

# 📡 WebSocket System

On every crowd update, the server broadcasts:

```json
{
  "type": "crowd_update",
  "location_id": 1,
  "current_count": 85,
  "capacity_limit": 300,
  "occupancy_percentage": 28.3,
  "density_level": "MEDIUM"
}
```

This ensures real-time UI updates without page refresh.

---

# 🧠 Crowd Density Logic

```
Occupancy % = (Current Count / Capacity Limit) × 100
```

Thresholds:

* 🟢 Low: < 30%
* 🟡 Medium: 30% – 70%
* 🔴 High: > 80% (Alert Triggered)

---

# 🚨 Alert System

Alerts are automatically triggered when:

* Occupancy exceeds 80%
* Crowd increases more than 30% between intervals

Alerts can:

* Be viewed in dashboard
* Be resolved via API
* Send email notifications

---

# 🚀 Running Locally

```bash
git clone https://github.com/your-username/crowd_monitor.git
cd crowd_monitor
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

To start background AI detection:

```bash
python manage.py run_detection --mode yolo --interval 5
```

---

# 🌐 Production Deployment (Render)

* Use PostgreSQL
* Use Redis for Channels
* Set `DEBUG=False`
* Use Gunicorn with Uvicorn worker

Start command:

```bash
gunicorn crowd_monitor.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

---

# 🎓 What Was Developed in This Project?

This project demonstrates:

* Full-stack Django architecture
* ASGI-based real-time communication
* WebSocket broadcast system
* AI computer vision integration
* Scalable alerting mechanism
* Production cloud deployment
* Database + Redis integration
* REST API design

It reflects production-level system design practices.

---

# 🔮 Future Enhancements

* Live CCTV integration
* Predictive crowd forecasting (ML models)
* SMS alerts (Twilio)
* Role-based access control
* Multi-location analytics dashboard
* Custom-trained YOLO model

---

# 👨‍💻 Developer

Gouse Velluri
Full Stack Developer | Django | Real-Time Systems | AI Integration

