"""
VisionGuard Event Engine.
Manages and evaluates plugin-based event rules against active object tracks.
"""

from typing import Dict, List, Optional
from visionguard.config.config_manager import EventsConfig
from visionguard.core.models import Event, FrameData, Region, Track
from visionguard.events.base_plugin import BaseEventPlugin
from visionguard.events.plugins.abnormal_motion import AbnormalMotionPlugin
from visionguard.events.plugins.crowd_threshold import CrowdThresholdPlugin
from visionguard.events.plugins.intrusion import IntrusionPlugin
from visionguard.events.plugins.line_crossing import LineCrossingPlugin
from visionguard.events.plugins.loitering import LoiteringPlugin
from visionguard.events.plugins.region_entry import RegionEntryPlugin
from visionguard.events.plugins.region_exit import RegionExitPlugin
from visionguard.events.plugins.removed_object import RemovedObjectPlugin
from visionguard.events.plugins.stationary import StationaryPlugin
from visionguard.logging.logger import logger


class EventEngine:
    """Core Event Engine orchestrating registered event detection plugins."""

    def __init__(self, events_config: Optional[EventsConfig] = None) -> None:
        self.plugins: Dict[str, BaseEventPlugin] = {}
        self.events_config = events_config or EventsConfig()
        self._register_default_plugins()

    def _register_default_plugins(self) -> None:
        p_cfgs = self.events_config.plugins

        plugin_classes = {
            "line_crossing": LineCrossingPlugin,
            "region_entry": RegionEntryPlugin,
            "region_exit": RegionExitPlugin,
            "intrusion": IntrusionPlugin,
            "loitering": LoiteringPlugin,
            "stationary": StationaryPlugin,
            "removed_object": RemovedObjectPlugin,
            "abnormal_motion": AbnormalMotionPlugin,
            "crowd_threshold": CrowdThresholdPlugin,
        }

        for name, cls in plugin_classes.items():
            cfg = p_cfgs.get(name)
            plugin_instance = cls(plugin_config=cfg)
            self.plugins[name] = plugin_instance
            logger.info(f"EventEngine: Registered plugin '{name}' (Enabled: {plugin_instance.config.enabled})")

    def register_plugin(self, plugin: BaseEventPlugin) -> None:
        self.plugins[plugin.name] = plugin
        logger.info(f"EventEngine: Custom plugin '{plugin.name}' registered.")

    def process_frame(
        self,
        tracks: List[Track],
        frame_data: FrameData,
        regions: List[Region],
    ) -> List[Event]:
        all_events: List[Event] = []

        for name, plugin in self.plugins.items():
            if plugin.config.enabled:
                try:
                    events = plugin.evaluate(tracks, frame_data, regions)
                    if events:
                        all_events.extend(events)
                except Exception as e:
                    logger.error(f"EventEngine: Exception evaluating plugin '{name}': {e}")

        return all_events
