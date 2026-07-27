"""Loitering Event Plugin."""
import time
from typing import Dict, List, Tuple
from visionguard.core.models import Event, FrameData, Region, RegionType, SeverityLevel, Track
from visionguard.events.base_plugin import BaseEventPlugin
from visionguard.regions.region_manager import RegionManager


class LoiteringPlugin(BaseEventPlugin):
    def __init__(self, plugin_config=None) -> None:
        super().__init__("loitering", plugin_config)
        self.entry_timestamps: Dict[Tuple[int, str], float] = {}

    def evaluate(self, tracks: List[Track], frame_data: FrameData, regions: List[Region]) -> List[Event]:
        events: List[Event] = []
        if not self.config.enabled:
            return events

        threshold_sec = self.config.threshold_sec or 5.0
        target_zones = self.config.target_zones or []
        poly_regions = [
            r for r in regions
            if r.region_type in (RegionType.POLYGON, RegionType.ROI) and (not target_zones or r.id in target_zones)
        ]
        now = time.time()

        for track in tracks:
            for region in poly_regions:
                key = (track.track_id, region.id)
                is_inside = RegionManager.point_in_polygon(track.centroid, region.points)

                if is_inside:
                    if key not in self.entry_timestamps:
                        self.entry_timestamps[key] = now
                    else:
                        duration = now - self.entry_timestamps[key]
                        if duration >= threshold_sec:
                            cooldown_key = f"loitering_{track.track_id}_{region.id}"
                            if not self.is_in_cooldown(cooldown_key, now):
                                self.update_cooldown(cooldown_key, now)
                                events.append(
                                    Event(
                                        timestamp=now,
                                        camera_id=frame_data.camera_id,
                                        event_type="loitering",
                                        severity=SeverityLevel.WARNING,
                                        object_id=track.track_id,
                                        object_class=track.class_name,
                                        confidence=track.confidence,
                                        zone_id=region.id,
                                        zone_name=region.name,
                                        metadata={"duration_sec": round(duration, 1), "location": track.centroid},
                                    )
                                )
                else:
                    self.entry_timestamps.pop(key, None)
        return events
