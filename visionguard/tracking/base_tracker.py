"""
VisionGuard Abstract Tracker Interface.
Satisfies Recommendation #4 (Abstract Tracker). Isolates the Multi-Object Tracking
algorithm from the rest of the analytics pipeline.
"""

from abc import ABC, abstractmethod
from typing import List
import numpy as np
from visionguard.core.models import Detection, Track


class BaseTracker(ABC):
    """Abstract Base Class for Multi-Object Trackers."""

    @abstractmethod
    def update(self, detections: List[Detection], image: np.ndarray) -> List[Track]:
        """
        Updates internal object tracks given frame detections and the raw image.
        Returns a list of active persistent Track objects.
        """
        pass

    @abstractmethod
    def reset(a) -> None:
        """Resets tracker state and tracklet memory."""
        pass
