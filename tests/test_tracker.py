"""Unit tests for ByteTrack Tracker."""
import numpy as np
import pytest
from visionguard.core.models import Detection, TrackState
from visionguard.tracking.byte_tracker import ByteTrackerPlugin, compute_iou

def test_iou_computation():
    box1 = (0, 0, 100, 100)
    box2 = (50, 50, 150, 150)
    iou = compute_iou(box1, box2)
    assert 0.14 < iou < 0.15

def test_bytetrack_update():
    tracker = ByteTrackerPlugin()
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    dets = [Detection(bbox=(10, 20, 100, 200), confidence=0.85, class_id=0, class_name="person")]

    tracks = tracker.update(dets, img)
    assert len(tracks) == 1
    assert tracks[0].track_id == 1
    assert tracks[0].state == TrackState.TRACKED
