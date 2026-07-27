"""Line Crossing Event Plugin."""
import time
from typing import Dict, List, Set, Tuple
from visionguard.core.models import Event, FrameData, Region, RegionType, SeverityLevel, Track
from visionguard.events.base_plugin import BaseEventPlugin
from visionguard.regions.region_manager import RegionManager


class LineCrossingPlugin(BaseEventPlugin):
    def __init__(self, plugin_config=None) -> None:
        super().__init__("line_crossing", plugin_config)
        self.track_sides: Dict[Tuple[int, str], float] = {}

    def evaluate(self, tracks: List[Track], frame_data: FrameData, regions: List[Region]) -> List[Event]:
        events: List[Event] = []
        if not self.config.enabled:
            return events

        line_regions = [r for r in regions if r.region_type == RegionType.LINE and len(r.points) >= 2]
        now = time.time()

        for track in tracks:
            if len(track.trajectory) < 2:
                continue

            p_curr = track.centroid
            p_prev = track.trajectory[-2]

            for line in line_regions:
                l_p1, l_p2 = line.points[0], line.points[1]

                side_curr = RegionManager.get_line_side(p_curr, l_p1, l_p2)
                side_prev = RegionManager.get_line_side(p_prev, l_p1, l_p2)

                track_key = (track.track_id, line.id)
                cooldown_key = f"{track.track_id}_{line.id}"

                if side_prev * side_curr < 0:  # Sign changed -> Crossed line
                    if not self.is_in_cooldown(cooldown_key, now):
                        self.update_cooldown(cooldown_key, now)
                        events.append(
                            Event(
                                timestamp=now,
                                camera_id=frame_data.camera_id,
                                event_type="line_crossing",
                                severity=SeverityLevel.INFO,
                                object_id=track.track_id,
                                object_class=track.class_name,
                                confidence=track.confidence,
                                zone_id=line.id,
                                zone_name=line.name,
                                metadata={
                                    "direction": line.direction,
                                    "crossing_point": p_curr,
                                },
                            )
                        )
                self.track_sides[track_key] = side_curr
        return events
