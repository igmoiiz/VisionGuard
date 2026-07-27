"""Unit tests for Event Engine and Plugins."""
import numpy as np
import pytest
from visionguard.core.models import FrameData, Region, RegionType, Track
from visionguard.events.event_engine import EventEngine
from visionguard.events.plugins.intrusion import IntrusionPlugin

def test_event_engine_initialization():
    ee = EventEngine()
    assert len(ee.plugins) == 9

def test_intrusion_plugin():
    plugin = IntrusionPlugin()
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    fd = FrameData(frame_id=1, camera_id="cam_01", image=img, width=640, height=480)

    region = Region(
        id="zone_restricted",
        name="Restricted Area",
        region_type=RegionType.POLYGON,
        points=[(0, 0), (200, 0), (200, 200), (0, 200)],
    )

    track = Track(
        track_id=1,
        class_id=0,
        class_name="person",
        confidence=0.9,
        bbox=(50, 50, 100, 100),
        centroid=(75.0, 75.0),
    )

    events = plugin.evaluate([track], fd, [region])
    assert len(events) == 1
    assert events[0].event_type == "intrusion"
