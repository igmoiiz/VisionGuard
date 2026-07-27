"""
VisionGuard: Production-Grade Intelligent Video Analytics Platform.
Unified CLI Entrypoint launching Video Processing Pipeline, REST API Server, and PySide6 Dashboard.
"""

import argparse
import sys
import time
from threading import Thread
import uvicorn
from visionguard.api.main import app as fastapi_app
from visionguard.bus.frame_bus import FrameBus
from visionguard.camera.stream_manager import StreamManager
from visionguard.config.config_manager import ConfigManager
from visionguard.core.resource_manager import ResourceManager
from visionguard.core.scheduler import create_default_scheduler
from visionguard.database.repository import EventRepository, MetricsRepository
from visionguard.database.session import DatabaseManager
from visionguard.events.event_dispatcher import EventDispatcher
from visionguard.events.event_engine import EventEngine
from visionguard.inference.yolo_engine import YOLOInferenceEngine
from visionguard.logging.logger import logger, setup_logger
from visionguard.metrics.metrics_collector import MetricsCollector
from visionguard.pipeline.pipeline import VideoPipeline
from visionguard.recording.recorder import VideoRecorder
from visionguard.regions.region_manager import RegionManager
from visionguard.rendering.renderer import AnnotationRenderer
from visionguard.tracking.byte_tracker import ByteTrackerPlugin


def build_system(config_path: str = "config/config.yaml", source_override: str = None) -> tuple:
    """Builds and wires all VisionGuard components using Dependency Injection."""
    # 1. Load Configuration & Logger
    config_mgr = ConfigManager(config_path)
    config = config_mgr.config
    setup_logger(level=config.system.get("log_level", "INFO"))

    logger.info("Initializing VisionGuard Production Platform...")

    if source_override and config.cameras:
        config.cameras[0].source = source_override

    # 2. Resource Manager & Task Scheduler
    res_mgr = ResourceManager.get_instance()
    scheduler = create_default_scheduler(
        recordings_dir=config.recording.output_dir,
        retention_days=config.recording.retention_days,
    )
    scheduler.start()

    # 3. Message Bus
    frame_bus = FrameBus()

    # 4. Database Persistence Layer
    db_mgr = DatabaseManager(db_url=config.database.url, echo=config.database.echo)
    event_repo = EventRepository(db_mgr.get_session)
    metrics_repo = MetricsRepository(db_mgr.get_session)

    # 5. Video Stream Ingestion
    cam_cfg = config.cameras[0] if config.cameras else None
    stream_mgr = StreamManager(
        camera_id=cam_cfg.id if cam_cfg else "cam_01",
        source=cam_cfg.source if cam_cfg else "0",
        fps_target=cam_cfg.fps_target if cam_cfg else 25.0,
        resolution=tuple(cam_cfg.resolution) if cam_cfg else (1280, 720),
    )

    # 6. Inference Engine & Tracker
    inf_engine = YOLOInferenceEngine(
        model_path=config.inference.model_path,
        cpu_threads=config.system.get("cpu_threads", 4),
    )
    tracker = ByteTrackerPlugin(
        track_high_thresh=config.tracking.track_high_thresh,
        track_low_thresh=config.tracking.track_low_thresh,
        new_track_thresh=config.tracking.new_track_thresh,
        match_thresh=config.tracking.match_thresh,
        track_buffer=config.tracking.track_buffer,
        max_trajectory_length=config.tracking.max_trajectory_length,
    )

    # 7. Region & Event Engines
    region_mgr = RegionManager(config.regions)
    event_engine = EventEngine(config.events)
    event_dispatcher = EventDispatcher(
        frame_bus=frame_bus,
        snapshots_dir=config.recording.snapshots_dir,
    )

    # Automatically persist triggered events to DB via FrameBus
    frame_bus.subscribe_callback("events", lambda ev: event_repo.save_event(ev))

    # 8. Renderer, Recorder & Metrics
    renderer = AnnotationRenderer()
    recorder = VideoRecorder(config.recording)
    metrics_collector = MetricsCollector(config.metrics.history_buffer_size)

    # 9. Assemble Pipeline
    pipeline = VideoPipeline(
        stream_manager=stream_mgr,
        inference_engine=inf_engine,
        tracker=tracker,
        region_manager=region_mgr,
        event_engine=event_engine,
        event_dispatcher=event_dispatcher,
        renderer=renderer,
        recorder=recorder,
        metrics_collector=metrics_collector,
        frame_bus=frame_bus,
        config=config,
    )

    res_mgr.register_service("pipeline", pipeline)
    return pipeline, frame_bus, config


def run_api_server(host: str, port: int):
    logger.info(f"Starting REST API Server on http://{host}:{port} (OpenAPI Docs: http://{host}:{port}/docs)...")
    uvicorn.run(fastapi_app, host=host, port=port, log_level="warning")


def main():
    parser = argparse.ArgumentParser(description="VisionGuard Intelligent Video Analytics Platform")
    parser.add_argument("--mode", choices=["all", "pipeline", "api", "gui"], default="all", help="Execution mode")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config.yaml")
    parser.add_argument("--source", default=None, help="Override video stream source (e.g. 0, RTSP URL, MP4 file)")
    args = parser.parse_args()

    pipeline, frame_bus, config = build_system(args.config, args.source)

    if args.mode in ("all", "pipeline"):
        pipeline.start()

    if args.mode in ("all", "api"):
        api_thread = Thread(
            target=run_api_server,
            args=(config.api.host, config.api.port),
            daemon=True,
            name="vg_api",
        )
        api_thread.start()

    if args.mode in ("all", "gui"):
        from visionguard.dashboard.app import launch_dashboard
        launch_dashboard(frame_bus=frame_bus)
    else:
        logger.info("VisionGuard running in headless CLI mode. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            logger.info("Shutting down VisionGuard...")
            pipeline.stop()


if __name__ == "__main__":
    main()
