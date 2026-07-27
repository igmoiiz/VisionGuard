"""
VisionGuard Abstract Video Stream Interface.
Defines standard frame capture, control flow, and metadata retrieval for video sources.
"""

from abc import ABC, abstractmethod
from typing import Optional
from visionguard.core.models import CameraState, FrameData


class BaseStream(ABC):
    """Abstract Base Class for Video Stream Readers."""

    @abstractmethod
    def start(self) -> None:
        """Starts frame ingestion thread."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stops frame ingestion and releases hardware resources."""
        pass

    @abstractmethod
    def read_frame(self) -> Optional[FrameData]:
        """Returns the latest captured FrameData object."""
        pass

    @abstractmethod
    def get_state(self) -> CameraState:
        """Returns current CameraState."""
        pass
