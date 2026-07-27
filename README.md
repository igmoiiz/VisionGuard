# VisionGuard: Production-Grade Intelligent Video Analytics Platform

**VisionGuard** is a commercial-grade, modular, scalable computer vision platform engineered to analyze live camera streams (Webcams, USB cameras, RTSP, IP streams) and recorded video files in real time.

Designed to operate efficiently on modest CPU-only hardware (Intel Core i5, 8GB RAM, no CUDA GPU required), VisionGuard implements enterprise software design patterns, high-performance multi-threading, and modular abstractions.

---

## 🌟 Key Features & Architecture

* **Shared Core Data Models**: Strongly typed Pydantic v2 objects (`FrameData`, `Detection`, `Track`, `Region`, `Event`, `PerformanceMetrics`) exchanged across all pipeline layers.
* **CPU-Optimized YOLO11 Inference Engine**: Uses PyTorch thread tuning (`torch.set_num_threads`) and frame skipping to achieve real-time throughput on CPU hardware.
* **ByteTrack Multi-Object Tracking**: Persistent object tracking across lost frame windows, maintaining trajectory history, velocity vectors, and stationary duration.
* **Plugin-Based Event Engine**: Modular plugins for 9 distinct event rules:
  1. **Line Crossing**: Directional boundary crossing.
  2. **Region Entry**: Polygon area entry.
  3. **Region Exit**: Polygon area exit.
  4. **Intrusion**: Unauthorized presence in restricted zones.
  5. **Loitering**: Object presence exceeding configurable duration thresholds.
  6. **Stationary Object**: Object remaining static over time.
  7. **Removed Object**: Unintended disappearance of static items.
  8. **Abnormal Motion**: Velocity and direction anomaly detection.
  9. **Crowd Threshold Alert**: Zone capacity limit violation.
* **Publish/Subscribe Frame Bus**: Asynchronous message bus decoupling stream ingestion, AI inference, tracking, event processing, recording, and UI/API subscribers.
* **Modular Annotation Renderer**: Layered OpenCV visual overlays (Regions ➔ Trajectories ➔ Bounding Boxes ➔ Event Alerts ➔ OSD Telemetry).
* **Automated Recording System**: Event-triggered pre/post ring-buffer recording, snapshot extraction, and disk retention cleanup.
* **REST API & WebSockets**: FastAPI server providing OpenAPI docs (`/docs`), camera management, event query filters, and WebSocket video streaming.
* **PySide6 Desktop Dashboard**: Dark-themed PySide6 desktop GUI with 6 dedicated views (Home Live Feed, Analytics Charts, Event Log Browser, Settings, Telemetry Gauges, Live Log Stream).
* **Automatic Synthetic Stream Fallback**: Automatically activates an animated synthetic video generator when physical webcam hardware is inaccessible.

---

## 📁 System Architecture & Directory Structure

```
VisionGuard/
├── config/
│   └── config.yaml               # Schema-versioned configuration (v1.0)
├── main.py                       # Unified CLI Launcher (GUI, API, Pipeline)
├── requirements.txt              # Production dependencies
├── visionguard/
│   ├── core/                     # Shared Foundation & Abstractions
│   │   ├── models.py             # Pydantic v2 Core Data Models
│   │   ├── state_machine.py      # Camera & Track State Machines
│   │   ├── resource_manager.py   # Lifecycle, Thread Pool & Queue Manager
│   │   └── scheduler.py          # Background Maintenance Scheduler
│   ├── config/                   # Configuration System
│   │   └── config_manager.py     # Schema Validator & Version Migration
│   ├── logging/                  # Logging System
│   │   └── logger.py             # Loguru & Rich Console Formatter
│   ├── bus/                      # Pub/Sub Messaging Engine
│   │   └── frame_bus.py          # Asynchronous Multi-Subscriber Frame Bus
│   ├── inference/                # Inference Engine Layer
│   │   ├── base.py               # Abstract InferenceEngine Interface
│   │   ├── yolo_engine.py        # Ultralytics YOLO11 Engine
│   │   └── onnx_engine.py        # ONNX Runtime CPU Engine
│   ├── camera/                   # Video Ingestion Engine
│   │   ├── base_stream.py        # Stream Interface
│   │   ├── stream_manager.py     # OpenCV / RTSP / Webcam Grabber
│   │   └── synthetic_stream.py  # Synthetic Video Generator (Fallback)
│   ├── tracking/                 # Multi-Object Tracker Layer
│   │   ├── base_tracker.py       # Abstract BaseTracker Interface
│   │   └── byte_tracker.py       # ByteTrack Plugin Implementation
│   ├── regions/                  # Spatial Geometry & Regions
│   │   └── region_manager.py     # Polygon, Line, ROI Geometry Math
│   ├── events/                   # Plugin-Based Event Engine
│   │   ├── base_plugin.py        # BaseEventPlugin Interface
│   │   ├── event_engine.py       # Event Engine Manager
│   │   ├── event_dispatcher.py   # Event Broadcaster & Storage Router
│   │   └── plugins/              # Pluggable Event Detectors
│   ├── analytics/                # Motion & Spatial Analytics
│   │   └── motion_analytics.py   # Heatmap, Trajectory & Flow Stats
│   ├── rendering/                # Modular Annotation Renderer
│   │   └── renderer.py           # Layered Frame Overlay Visualizer
│   ├── recording/                # Automated Video & Snapshot Recorder
│   │   └── recorder.py           # Pre/Post Event Ring-Buffer Recorder
│   ├── metrics/                  # Centralized System Metrics
│   │   ├── cpu.py                # CPU Usage Collector
│   │   ├── memory.py             # RAM Allocation Monitor
│   │   ├── fps.py                # Frame-per-Second Calculator
│   │   └── latency.py            # Latency Profiler
│   ├── database/                 # Database Persistence Layer
│   │   ├── models.py             # SQLAlchemy ORM Data Models
│   │   ├── session.py            # SQLite / DB Engine & Session Factory
│   │   └── repository.py         # Repository Pattern (DAO)
│   ├── pipeline/                 # Core Pipeline Orchestrator
│   │   └── pipeline.py           # Dependency-Injected Pipeline Execution
│   ├── api/                      # REST API & WebSocket Server
│   │   ├── main.py               # FastAPI App Engine
│   │   └── routes/               # API Endpoints (/cameras, /events, /metrics)
│   └── dashboard/                # PySide6 Desktop Dashboard
│       ├── app.py                # Main PySide6 Application Window
│       └── ui/                   # Modular Qt Dashboard Views
└── tests/                        # Pytest Unit Test Suite
```

---

## ⚙️ Installation & Quickstart

### 1. Activate Environment & Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch Full Platform (GUI + Pipeline + REST API)
```bash
python main.py --mode all
```

### 3. Execution Modes
* **Full Application (Default)**: `python main.py --mode all`
* **Desktop Dashboard Only**: `python main.py --mode gui`
* **REST API Server Only**: `python main.py --mode api`
* **Headless Analytics Engine**: `python main.py --mode pipeline`
* **Custom Video Source**: `python main.py --source video.mp4`

---

## 📡 REST API & Interactive Documentation

When VisionGuard is running, the REST API is served on `http://127.0.0.1:8000`.

* **Interactive Swagger UI Docs**: `http://127.0.0.1:8000/docs`
* **Health Check**: `GET http://127.0.0.1:8000/api/v1/system/health`
* **Live Telemetry**: `GET http://127.0.0.1:8000/api/v1/metrics/live`
* **Event Search**: `GET http://127.0.0.1:8000/api/v1/events`

---

## 🧪 Running Unit Tests

Run the `pytest` test suite:
```bash
pytest tests/
```

---

## 📄 License
Production Software Architecture — VisionGuard Project.
