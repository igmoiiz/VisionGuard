"""
VisionGuard Region Manager & Spatial Geometry.
Provides high-performance spatial geometry algorithms (Point-in-Polygon, Line Crossing, ROI Masks)
for evaluating object trajectories against configured regions.
"""

from typing import List, Optional, Tuple
import cv2
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from visionguard.config.config_manager import RegionConfig
from visionguard.core.models import Region, RegionType
from visionguard.logging.logger import logger


class RegionManager:
    """Manages geometric regions and spatial containment evaluations."""

    def __init__(self, region_configs: Optional[List[RegionConfig]] = None) -> None:
        self.regions: List[Region] = []
        if region_configs:
            for rc in region_configs:
                self.add_region_from_config(rc)

    def add_region_from_config(self, rc: RegionConfig) -> None:
        r_type = RegionType(rc.type)
        points_tuples = [(float(p[0]), float(p[1])) for p in rc.points]
        color_tuple = (int(rc.color[0]), int(rc.color[1]), int(rc.color[2]))

        region = Region(
            id=rc.id,
            name=rc.name,
            region_type=r_type,
            points=points_tuples,
            direction=rc.direction,
            color=color_tuple,
            enabled=rc.enabled,
        )
        self.regions.append(region)
        logger.info(f"RegionManager: Added region '{region.name}' ({region.region_type.value})")

    def get_enabled_regions(self) -> List[Region]:
        return [r for r in self.regions if r.enabled]

    @staticmethod
    def point_in_polygon(point: Tuple[float, float], polygon_points: List[Tuple[float, float]]) -> bool:
        """Determines if a 2D point is inside a polygon using Shapely/OpenCV."""
        if len(polygon_points) < 3:
            return False
        try:
            poly = Polygon(polygon_points)
            p = Point(point)
            return poly.contains(p) or poly.touches(p)
        except Exception:
            # OpenCV fallback
            pts = np.array(polygon_points, dtype=np.int32)
            res = cv2.pointPolygonTest(pts, (float(point[0]), float(point[1])), False)
            return res >= 0

    @staticmethod
    def line_intersects_segment(
        trajectory_p1: Tuple[float, float],
        trajectory_p2: Tuple[float, float],
        line_p1: Tuple[float, float],
        line_p2: Tuple[float, float],
    ) -> bool:
        """Determines if a trajectory segment intersects a counting line."""
        try:
            traj_line = LineString([trajectory_p1, trajectory_p2])
            gate_line = LineString([line_p1, line_p2])
            return traj_line.intersects(gate_line)
        except Exception:
            return False

    @staticmethod
    def get_line_side(point: Tuple[float, float], line_p1: Tuple[float, float], line_p2: Tuple[float, float]) -> float:
        """Determines which side of a line segment a point lies on (cross product > 0 or < 0)."""
        return (line_p2[0] - line_p1[0]) * (point[1] - line_p1[1]) - (line_p2[1] - line_p1[1]) * (point[0] - line_p1[0])
