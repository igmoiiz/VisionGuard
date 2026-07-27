"""
VisionGuard Event Dispatcher.
Routes triggered events to database storage, saves snapshot files,
logs alerts, and broadcasts to FrameBus subscribers.
"""

from pathlib import Path
from typing import List, Optional
import cv2
from visionguard.bus.frame_bus import FrameBus
from visionguard.core.models import Event, FrameData
from visionguard.logging.logger import logger


class EventDispatcher:
    """Asynchronous event router and snapshot persistence generator."""

    def __init__(
        self,
        frame_bus: Optional[FrameBus] = None,
        snapshots_dir: str = "data/snapshots",
    ) -> None:
        self.frame_bus = frame_bus
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def dispatch(self, events: List[Event], frame_data: FrameData) -> None:
        for event in events:
            # 1. Save Snapshot Image
            snapshot_filename = f"event_{event.event_type}_{event.camera_id}_{int(event.timestamp)}.jpg"
            snapshot_path = self.snapshots_dir / snapshot_filename

            try:
                # Save annotated or raw image
                img_to_save = frame_data.annotated_image if frame_data.annotated_image is not None else frame_data.image
                cv2.imwrite(str(snapshot_path), img_to_save)
                event.snapshot_path = str(snapshot_path)
            except Exception as e:
                logger.error(f"EventDispatcher: Failed to save snapshot '{snapshot_path}': {e}")

            # 2. Log Alert
            logger.warning(
                f"EVENT DETECTED [{event.severity.value.upper()}] - Camera: {event.camera_id} | Type: {event.event_type} | "
                f"Object: {event.object_class} (#{event.object_id}) | Zone: {event.zone_name or 'Global'}"
            )

            # 3. Publish to FrameBus
            if self.frame_bus:
                self.frame_bus.publish("events", event)
