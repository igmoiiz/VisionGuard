"""Crowd Threshold Alert Event Plugin."""
import time
from typing import List
from visionguard.core.models import Event, FrameData, Region, RegionType, SeverityLevel, Track
from visionguard.events.base_plugin import BaseEventPlugin
from visionguard.regions.region_manager import RegionManager


class CrowdThresholdPlugin(BaseEventPlugin):
    def __init__(self, plugin_config=None) -> None:
        super().__init__("crowd_threshold", plugin_config)

    def evaluate(self, tracks: List[Track], frame_data: FrameData, regions: List[Region]) -> List[Event]:
        events: List[Event] = []
        if not self.config.enabled:
            return events

        max_count = self.config.max_count or 5
        target_zones = self.config.target_zones or []
        poly_regions = [
            r for r in regions
            if r.region_type in (RegionType.POLYGON, RegionType.ROI) and (not target_zones or r.id in target_zones)
        ]
        now = time.time()

        for region in poly_regions:
            inside_tracks = [t for t in tracks if RegionManager.point_in_polygon(t.centroid, region.points)]
            count = len(inside_tracks)

            if count > max_count:
                cooldown_key = f"crowd_{region.id}"
                if not self.is_in_cooldown(cooldown_key, now):
                    self.update_cooldown(cooldown_key, now)
                    events.append(
                        Event(
                            timestamp=now,
                            camera_id=frame_data.camera_id,
                            event_type="crowd_threshold_alert",
                            severity=SeverityLevel.ALERT,
                            zone_id=region.id,
                            zone_name=region.name,
                            metadata={"object_count": count, "max_threshold": max_count},
                        )
                    )
        return events
