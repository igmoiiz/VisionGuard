"""Intrusion Detection Event Plugin."""
import time
from typing import List
from visionguard.core.models import Event, FrameData, Region, RegionType, SeverityLevel, Track
from visionguard.events.base_plugin import BaseEventPlugin
from visionguard.regions.region_manager import RegionManager


class IntrusionPlugin(BaseEventPlugin):
    def __init__(self, plugin_config=None) -> None:
        super().__init__("intrusion", plugin_config)

    def evaluate(self, tracks: List[Track], frame_data: FrameData, regions: List[Region]) -> List[Event]:
        events: List[Event] = []
        if not self.config.enabled:
            return events

        target_zones = self.config.target_zones or []
        poly_regions = [
            r for r in regions
            if r.region_type in (RegionType.POLYGON, RegionType.ROI) and (not target_zones or r.id in target_zones)
        ]
        now = time.time()

        for track in tracks:
            if self.config.target_classes and track.class_name not in self.config.target_classes:
                continue

            for region in poly_regions:
                if RegionManager.point_in_polygon(track.centroid, region.points):
                    cooldown_key = f"intrusion_{track.track_id}_{region.id}"
                    if not self.is_in_cooldown(cooldown_key, now):
                        self.update_cooldown(cooldown_key, now)
                        events.append(
                            Event(
                                timestamp=now,
                                camera_id=frame_data.camera_id,
                                event_type="intrusion",
                                severity=SeverityLevel.ALERT,
                                object_id=track.track_id,
                                object_class=track.class_name,
                                confidence=track.confidence,
                                zone_id=region.id,
                                zone_name=region.name,
                                metadata={"location": track.centroid},
                            )
                        )
        return events
