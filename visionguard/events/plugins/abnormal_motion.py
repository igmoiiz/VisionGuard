"""Abnormal Motion Event Plugin."""
import time
from typing import List
import numpy as np
from visionguard.core.models import Event, FrameData, Region, SeverityLevel, Track
from visionguard.events.base_plugin import BaseEventPlugin


class AbnormalMotionPlugin(BaseEventPlugin):
    def __init__(self, plugin_config=None) -> None:
        super().__init__("abnormal_motion", plugin_config)

    def evaluate(self, tracks: List[Track], frame_data: FrameData, regions: List[Region]) -> List[Event]:
        events: List[Event] = []
        if not self.config.enabled:
            return events

        thresh_velocity = self.config.velocity_threshold_px_per_sec or 250.0
        now = time.time()

        for track in tracks:
            vx, vy = track.velocity
            speed = float(np.hypot(vx, vy)) * frame_data.fps

            if speed >= thresh_velocity:
                cooldown_key = f"abnormal_{track.track_id}"
                if not self.is_in_cooldown(cooldown_key, now):
                    self.update_cooldown(cooldown_key, now)
                    events.append(
                        Event(
                            timestamp=now,
                            camera_id=frame_data.camera_id,
                            event_type="abnormal_motion",
                            severity=SeverityLevel.WARNING,
                            object_id=track.track_id,
                            object_class=track.class_name,
                            confidence=track.confidence,
                            metadata={"speed_px_per_sec": round(speed, 1), "location": track.centroid},
                        )
                    )
        return events
