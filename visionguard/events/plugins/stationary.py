"""Stationary Object Event Plugin."""
import time
from typing import List
from visionguard.core.models import Event, FrameData, Region, SeverityLevel, Track
from visionguard.events.base_plugin import BaseEventPlugin


class StationaryPlugin(BaseEventPlugin):
    def __init__(self, plugin_config=None) -> None:
        super().__init__("stationary", plugin_config)

    def evaluate(self, tracks: List[Track], frame_data: FrameData, regions: List[Region]) -> List[Event]:
        events: List[Event] = []
        if not self.config.enabled:
            return events

        threshold_sec = self.config.threshold_sec or 8.0
        now = time.time()

        for track in tracks:
            if track.stationary_duration_sec >= threshold_sec:
                cooldown_key = f"stationary_{track.track_id}"
                if not self.is_in_cooldown(cooldown_key, now):
                    self.update_cooldown(cooldown_key, now)
                    events.append(
                        Event(
                            timestamp=now,
                            camera_id=frame_data.camera_id,
                            event_type="stationary_object",
                            severity=SeverityLevel.WARNING,
                            object_id=track.track_id,
                            object_class=track.class_name,
                            confidence=track.confidence,
                            metadata={
                                "stationary_duration_sec": round(track.stationary_duration_sec, 1),
                                "location": track.centroid,
                            },
                        )
                    )
        return events
