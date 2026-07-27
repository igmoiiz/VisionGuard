"""Removed Object Event Plugin."""
import time
from typing import Dict, List
from visionguard.core.models import Event, FrameData, Region, SeverityLevel, Track, TrackState
from visionguard.events.base_plugin import BaseEventPlugin


class RemovedObjectPlugin(BaseEventPlugin):
    def __init__(self, plugin_config=None) -> None:
        super().__init__("removed_object", plugin_config)
        self.known_static_objects: Dict[int, float] = {}

    def evaluate(self, tracks: List[Track], frame_data: FrameData, regions: List[Region]) -> List[Event]:
        events: List[Event] = []
        if not self.config.enabled:
            return events

        threshold_sec = self.config.threshold_sec or 10.0
        now = time.time()
        active_ids = {t.track_id for t in tracks}

        for track in tracks:
            if track.stationary_duration_sec >= threshold_sec:
                self.known_static_objects[track.track_id] = now

        # Detect disappeared static objects
        missing_ids = [tid for tid, last_t in list(self.known_static_objects.items()) if tid not in active_ids]
        for tid in missing_ids:
            last_t = self.known_static_objects.pop(tid)
            if (now - last_t) < 5.0:  # Recently disappeared
                cooldown_key = f"removed_{tid}"
                if not self.is_in_cooldown(cooldown_key, now):
                    self.update_cooldown(cooldown_key, now)
                    events.append(
                        Event(
                            timestamp=now,
                            camera_id=frame_data.camera_id,
                            event_type="removed_object",
                            severity=SeverityLevel.ALERT,
                            object_id=tid,
                            metadata={"disappeared_timestamp": now},
                        )
                    )
        return events
