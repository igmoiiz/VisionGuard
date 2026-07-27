"""Region Exit Event Plugin."""
import time
from typing import Dict, List, Set, Tuple
from visionguard.core.models import Event, FrameData, Region, RegionType, SeverityLevel, Track
from visionguard.events.base_plugin import BaseEventPlugin
from visionguard.regions.region_manager import RegionManager


class RegionExitPlugin(BaseEventPlugin):
    def __init__(self, plugin_config=None) -> None:
        super().__init__("region_exit", plugin_config)
        self.inside_state: Set[Tuple[int, str]] = set()

    def evaluate(self, tracks: List[Track], frame_data: FrameData, regions: List[Region]) -> List[Event]:
        events: List[Event] = []
        if not self.config.enabled:
            return events

        poly_regions = [r for r in regions if r.region_type in (RegionType.POLYGON, RegionType.ROI)]
        now = time.time()

        for track in tracks:
            for region in poly_regions:
                key = (track.track_id, region.id)
                is_inside = RegionManager.point_in_polygon(track.centroid, region.points)

                if not is_inside and key in self.inside_state:
                    self.inside_state.remove(key)
                    cooldown_key = f"{track.track_id}_{region.id}"
                    if not self.is_in_cooldown(cooldown_key, now):
                        self.update_cooldown(cooldown_key, now)
                        events.append(
                            Event(
                                timestamp=now,
                                camera_id=frame_data.camera_id,
                                event_type="region_exit",
                                severity=SeverityLevel.INFO,
                                object_id=track.track_id,
                                object_class=track.class_name,
                                confidence=track.confidence,
                                zone_id=region.id,
                                zone_name=region.name,
                                metadata={"location": track.centroid},
                            )
                        )
                elif is_inside and key not in self.inside_state:
                    self.inside_state.add(key)
        return events
