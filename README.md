# VisionGuard: Production-Grade Intelligent Video Analytics Platform

**Owner & Creator**: [igmoiiz](https://github.com/igmoiiz/VisionGuard)

---

## 🛡️ Executive Summary

**VisionGuard** is a commercial-grade, modular, scalable computer vision platform engineered to analyze live camera streams (Webcams, USB cameras, RTSP, IP streams) and recorded video files in real time.

Designed to operate efficiently on modest CPU-only hardware (Intel Core i5, 8GB RAM, no CUDA GPU required), VisionGuard strictly implements enterprise software engineering design patterns, high-performance multi-threading, and modular abstractions.

---

## 🌟 Key Features & Innovations

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

## 🏗️ Enterprise Architecture (12 Core Design Patterns)

1. **Shared Core Data Models** (`visionguard/core/models.py` with Pydantic v2 objects).
2. **Plugin Architecture for Events** (`visionguard/events/plugins/` with `BaseEventPlugin` interface).
3. **Inference Engine Layer** (`InferenceEngine` base class ➔ `YOLOInferenceEngine` & `ONNXInferenceEngine`).
4. **Abstract Tracker Interface** (`BaseTracker` interface ➔ `ByteTrackerPlugin`).
5. **Publish/Subscribe Frame Bus** (`visionguard/bus/frame_bus.py` for decoupled asynchronous streaming).
6. **Centralized Metrics Module** (`visionguard/metrics/` for CPU, Memory, FPS, Latency).
7. **Modular Annotation Renderer** (`visionguard/rendering/renderer.py` for 5-layer OpenCV visuals).
8. **System Resource Manager** (`visionguard/core/resource_manager.py` for thread pools, queues, lifecycle & shutdown).
9. **Task Scheduler** (`visionguard/core/scheduler.py` for video cleanup, DB WAL checkpointing, vacuum, stats refresh).
10. **State Machines** (`visionguard/core/state_machine.py` for Camera & Track state transitions).
11. **Configuration Schema Versioning** (`config.yaml` version `1.0` with migration hooks).
12. **Dependency Injection Architecture** (`Pipeline` & services configured via constructor injection).

---

## 📁 System Folder Structure

```
VisionGuard/
├── config/
│   └── config.yaml               # Schema-versioned configuration (v1.0)
├── main.py                       # Unified CLI Launcher (GUI, API, Pipeline)
├── requirements.txt              # Production dependencies
├── LICENSE                       # Custom Attribution License
├── .gitignore                    # Automated Git Ignore rules
├── README.md                     # Documentation
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

### 1. Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch Platform
```bash
# Run complete system (GUI + Pipeline + REST API)
PYTHONPATH=. python main.py --mode all

# Desktop GUI only
PYTHONPATH=. python main.py --mode gui

# Headless analytics engine only
PYTHONPATH=. python main.py --mode pipeline

# REST API Server only
PYTHONPATH=. python main.py --mode api

# Custom video file input
PYTHONPATH=. python main.py --source my_video.mp4
```

---

## 📡 REST API Documentation

When running, FastAPI automatically serves interactive OpenAPI documentation:

* **Swagger UI**: `http://127.0.0.1:8000/docs`
* **Health Check**: `GET http://127.0.0.1:8000/api/v1/system/health`
* **Live System Metrics**: `GET http://127.0.0.1:8000/api/v1/metrics/live`
* **Search Events**: `GET http://127.0.0.1:8000/api/v1/events`

---

## 🧪 Testing

Execute the unit test suite:
```bash
PYTHONPATH=. ./.venv/bin/pytest tests/ -v
```

---

## 📜 License & Attribution

Copyright (c) 2026 **igmoiiz**.

Any permitted use, study, or modification of this code **MUST** explicitly cite and attribute the original author and owner: **igmoiiz** (Repository: https://github.com/igmoiiz/VisionGuard). Non-permitted or unattributed redistribution is strictly prohibited. See the [`LICENSE`](LICENSE) file for complete details.
