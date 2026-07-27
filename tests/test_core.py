"""Unit tests for Core Data Models and State Machines."""
import numpy as np
import pytest
from visionguard.core.models import Detection, FrameData, Track, TrackState, CameraState
from visionguard.core.state_machine import CameraStateMachine, TrackStateMachine

def test_frame_data():
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    fd = FrameData(frame_id=1, camera_id="cam_01", image=img, width=640, height=480)
    assert fd.frame_id == 1
    assert fd.width == 640

def test_detection_model():
    det = Detection(bbox=(10, 20, 100, 200), confidence=0.85, class_id=0, class_name="person")
    assert det.width == 90
    assert det.height == 180
    assert det.centroid == (55.0, 110.0)

def test_camera_state_machine():
    sm = CameraStateMachine("cam_01")
    assert sm.current_state == CameraState.DISCONNECTED
    sm.transition_to(CameraState.STREAMING)
    assert sm.current_state == CameraState.STREAMING
