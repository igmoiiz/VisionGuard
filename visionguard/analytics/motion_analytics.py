"""
VisionGuard Motion & Spatial Analytics.
Generates 2D motion heatmaps, traffic density grids, path trajectory overlays,
and object flow statistics.
"""

from collections import defaultdict
from typing import Dict, List, Tuple
import cv2
import numpy as np
from visionguard.core.models import Track


class MotionAnalytics:
    """Accumulates trajectory data to generate motion heatmaps and spatial analytics."""

    def __init__(self, width: int = 1280, height: int = 720, decay_factor: float = 0.995) -> None:
        self.width = width
        self.height = height
        self.decay_factor = decay_factor
        self.heatmap_grid = np.zeros((height, width), dtype=np.float32)
        self.class_counts: Dict[str, int] = defaultdict(int)

    def update(self, tracks: List[Track]) -> None:
        # Apply exponential temporal decay
        self.heatmap_grid *= self.decay_factor

        for track in tracks:
            cx, cy = int(track.centroid[0]), int(track.centroid[1])
            if 0 <= cx < self.width and 0 <= cy < self.height:
                # Add 2D Gaussian point accumulation
                cv2.circle(self.heatmap_grid, (cx, cy), 15, 1.0, -1)
                self.class_counts[track.class_name] += 1

    def generate_heatmap_overlay(self, base_image: np.ndarray, alpha: float = 0.5) -> np.ndarray:
        """Blends normalized 2D motion heatmap over a base video frame."""
        if base_image is None or base_image.shape[0] != self.height or base_image.shape[1] != self.width:
            return base_image

        norm_grid = cv2.normalize(self.heatmap_grid, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        color_heatmap = cv2.applyColorMap(norm_grid, cv2.COLORMAP_JET)

        blended = cv2.addWeighted(base_image, 1.0 - alpha, color_heatmap, alpha, 0)
        return blended

    def get_class_breakdown(a) -> Dict[str, int]:
        return dict(self.class_counts)
