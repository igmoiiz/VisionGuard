"""
VisionGuard Abstract Event Plugin Interface.
Satisfies Recommendation #2 (Plugin Architecture for Events). All event types
implement this interface for seamless modular addition of new analytics rules.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from visionguard.config.config_manager import EventPluginConfig
from visionguard.core.models import Event, FrameData, Region, Track


class BaseEventPlugin(ABC):
    """Abstract Base Class for Event Engine Analytics Plugins."""

    def __init__(self, name: str, plugin_config: Optional[EventPluginConfig] = None) -> None:
        self.name = name
        self.config = plugin_config or EventPluginConfig()
        self.cooldown_tracker: Dict[str, float] = {}  # Key -> last_triggered_timestamp

    def is_in_cooldown(self, key: str, current_time: float) -> bool:
        last_time = self.cooldown_tracker.get(key, 0.0)
        return (current_time - last_time) < self.config.cooldown_sec

    def update_cooldown(self, key: str, current_time: float) -> None:
        self.cooldown_tracker[key] = current_time

    @abstractmethod
    def evaluate(
        self,
        tracks: List[Track],
        frame_data: FrameData,
        regions: List[Region],
    ) -> List[Event]:
        """
        Evaluates active object tracks against frame data and geometrical regions.
        Returns a list of triggered Event objects.
        """
        pass
