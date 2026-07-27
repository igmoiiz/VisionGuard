"""
VisionGuard Video & Snapshot Recorder.
Threaded OpenCV VideoWriter supporting continuous recording, event-triggered
pre/post ring-buffer recording, snapshot generation, and retention management.
"""

from collections import deque
from pathlib import Path
import time
from threading import Thread
from typing import Dict, List, Optional
import cv2
import numpy as np
from visionguard.config.config_manager import RecordingConfig
from visionguard.core.models import Event, FrameData
from visionguard.logging.logger import logger


class VideoRecorder:
    """Automated video stream recorder with pre/post event buffer handling."""

    def __init__(self, config: Optional[RecordingConfig] = None) -> None:
        self.config = config or RecordingConfig()
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Pre-event ring buffer (stores past frames)
        max_buffer_frames = int(self.config.pre_event_buffer_sec * 25.0)
        self.ring_buffer: deque[np.ndarray] = deque(maxlen=max_buffer_frames)

        self.is_event_recording = False
        self.event_record_stop_time = 0.0
        self.writer: Optional[cv2.VideoWriter] = None
        self.current_video_path: Optional[Path] = None

    def process_frame(self, frame_data: FrameData, events: List[Event]) -> None:
        if not self.config.enabled:
            return

        img = frame_data.annotated_image if frame_data.annotated_image is not None else frame_data.image
        self.ring_buffer.append(img.copy())

        now = time.time()

        # Trigger event recording if an alert event occurs
        if self.config.event_triggered and events:
            self._start_event_recording(frame_data, now)

        # Write frame to active video file
        if self.is_event_recording:
            if self.writer is not None:
                self.writer.write(img)

            # Check if post-event buffer duration has expired
            if now >= self.event_record_stop_time:
                self._stop_event_recording()

    def _start_event_recording(self, frame_data: FrameData, now: float) -> None:
        self.event_record_stop_time = now + self.config.post_event_buffer_sec

        if not self.is_event_recording:
            self.is_event_recording = True
            filename = f"event_rec_{frame_data.camera_id}_{int(now)}.mp4"
            self.current_video_path = self.output_dir / filename

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            h, w = frame_data.image.shape[:2]
            self.writer = cv2.VideoWriter(str(self.current_video_path), fourcc, 25.0, (w, h))

            logger.info(f"VideoRecorder: Started event recording '{self.current_video_path}'")

            # Dump pre-event ring buffer frames into writer
            for buffered_img in list(self.ring_buffer):
                self.writer.write(buffered_img)

    def _stop_event_recording(self) -> None:
        if self.writer is not None:
            self.writer.release()
            self.writer = None
            logger.info(f"VideoRecorder: Stopped event recording '{self.current_video_path}'")
        self.is_event_recording = False

    def close(self) -> None:
        if self.writer is not None:
            self.writer.release()
            self.writer = None
