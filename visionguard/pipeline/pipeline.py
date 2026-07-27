"""
VisionGuard Processing Pipeline.
Satisfies Recommendation #12 (Dependency Injection Architecture). Orchestrates video stream ingestion,
YOLO detection, ByteTrack multi-object tracking, region math, event evaluation, annotation rendering,
recording, metrics profiling, and Pub/Sub frame bus publication.
"""

import time
from threading import Thread
from typing import List, Optional
from visionguard.analytics.motion_analytics import MotionAnalytics
from visionguard.bus.frame_bus import FrameBus
from visionguard.camera.base_stream import BaseStream
from visionguard.config.config_manager import AppConfig
from visionguard.core.models import Detection, Event, FrameData, Track
from visionguard.events.event_dispatcher import EventDispatcher
from visionguard.events.event_engine import EventEngine
from visionguard.inference.base import InferenceEngine
from visionguard.logging.logger import logger
from visionguard.metrics.metrics_collector import MetricsCollector
from visionguard.recording.recorder import VideoRecorder
from visionguard.regions.region_manager import RegionManager
from visionguard.rendering.renderer import AnnotationRenderer
from visionguard.tracking.base_tracker import BaseTracker


class VideoPipeline:
    """Dependency-injected Video Analytics Pipeline."""

    def __init__(
        self,
        stream_manager: BaseStream,
        inference_engine: InferenceEngine,
        tracker: BaseTracker,
        region_manager: RegionManager,
        event_engine: EventEngine,
        event_dispatcher: EventDispatcher,
        renderer: AnnotationRenderer,
        recorder: VideoRecorder,
        metrics_collector: MetricsCollector,
        frame_bus: FrameBus,
        config: AppConfig,
    ) -> None:
        self.stream_manager = stream_manager
        self.inference_engine = inference_engine
        self.tracker = tracker
        self.region_manager = region_manager
        self.event_engine = event_engine
        self.event_dispatcher = event_dispatcher
        self.renderer = renderer
        self.recorder = recorder
        self.metrics_collector = metrics_collector
        self.frame_bus = frame_bus
        self.config = config

        self.motion_analytics = MotionAnalytics(
            width=config.cameras[0].resolution[0] if config.cameras else 1280,
            height=config.cameras[0].resolution[1] if config.cameras else 720,
        )

        self.running = False
        self._thread: Optional[Thread] = None
        self.last_tracks: List[Track] = []

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.stream_manager.start()
        self._thread = Thread(target=self._processing_loop, daemon=True, name="vg_pipeline")
        self._thread.start()
        logger.info("VideoPipeline: Processing pipeline loop started.")

    def stop(self) -> None:
        self.running = False
        self.stream_manager.stop()
        self.recorder.close()
        logger.info("VideoPipeline: Stopped pipeline.")

    def _processing_loop(self) -> None:
        frame_skip = self.config.inference.frame_skip
        frame_count = 0

        while self.running:
            frame_data = self.stream_manager.read_frame()
            if frame_data is None:
                time.sleep(0.005)
                continue

            t_start = time.time()
            self.metrics_collector.tick_frame()
            frame_count += 1

            # Step 1: Object Detection (with frame skip for CPU efficiency)
            detections: List[Detection] = []
            if frame_count % frame_skip == 0:
                t_det_start = time.time()
                detections = self.inference_engine.predict(
                    image=frame_data.image,
                    confidence_threshold=self.config.inference.confidence_threshold,
                    iou_threshold=self.config.inference.iou_threshold,
                    target_classes=self.config.inference.target_classes,
                )
                self.metrics_collector.record_latency("detection", (time.time() - t_det_start) * 1000.0)

            # Step 2: Multi-Object Tracking
            t_track_start = time.time()
            tracks = self.tracker.update(detections, frame_data.image)
            self.last_tracks = tracks
            self.metrics_collector.record_latency("tracking", (time.time() - t_track_start) * 1000.0)

            # Step 3: Motion Analytics update
            self.motion_analytics.update(tracks)

            # Step 4: Event Engine evaluation
            enabled_regions = self.region_manager.get_enabled_regions()
            events: List[Event] = self.event_engine.process_frame(tracks, frame_data, enabled_regions)

            # Step 5: Event Dispatching (Snapshot, DB, FrameBus)
            if events:
                self.event_dispatcher.dispatch(events, frame_data)

            # Step 6: Annotation Rendering
            perf_metrics = self.metrics_collector.collect()
            annotated_img = self.renderer.render(
                frame_data=frame_data,
                tracks=tracks,
                regions=enabled_regions,
                active_events=events,
                metrics=perf_metrics,
            )
            frame_data.annotated_image = annotated_img

            # Step 7: Video Recording
            self.recorder.process_frame(frame_data, events)

            # Step 8: Publish frame & metrics to Pub/Sub FrameBus
            self.frame_bus.publish("frames", frame_data)
            self.frame_bus.publish("metrics", perf_metrics)

            pipeline_latency = (time.time() - t_start) * 1000.0
            self.metrics_collector.record_latency("pipeline", pipeline_latency)
