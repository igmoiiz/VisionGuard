"""
VisionGuard State Machines.
Provides explicit, thread-safe state machines for Camera stream connections
and Tracker lifecycle states with event callbacks on state transitions.
"""

from threading import Lock
from typing import Callable, List, Optional
from visionguard.core.models import CameraState, TrackState
from visionguard.logging.logger import logger


class CameraStateMachine:
    """Manages Camera connection lifecycle transitions."""
    def __init__(self, camera_id: str, initial_state: CameraState = CameraState.DISCONNECTED) -> None:
        self.camera_id = camera_id
        self._state = initial_state
        self._lock = Lock()
        self._listeners: List[Callable[[str, CameraState, CameraState], None]] = []

    @property
    def current_state(self) -> CameraState:
        with self._lock:
            return self._state

    def add_listener(self, callback: Callable[[str, CameraState, CameraState], None]) -> None:
        with self._lock:
            self._listeners.append(callback)

    def transition_to(self, new_state: CameraState, reason: Optional[str] = None) -> bool:
        with self._lock:
            old_state = self._state
            if old_state == new_state:
                return False

            self._state = new_state
            logger.info(f"Camera [{self.camera_id}] state: {old_state.value} -> {new_state.value}" + (f" ({reason})" if reason else ""))
            listeners = list(self._listeners)

        for callback in listeners:
            try:
                callback(self.camera_id, old_state, new_state)
            except Exception as e:
                logger.error(f"Error in camera state transition listener: {e}")
        return True


class TrackStateMachine:
    """Manages Multi-Object Track lifecycle transitions (NEW -> TRACKED -> LOST -> REMOVED)."""
    def __init__(self, track_id: int) -> None:
        self.track_id = track_id
        self._state = TrackState.NEW
        self._lock = Lock()

    @property
    def current_state(self) -> TrackState:
        with self._lock:
            return self._state

    def update_state(self, is_detected: bool, max_lost_frames: int = 30, lost_count: int = 0) -> TrackState:
        with self._lock:
            if is_detected:
                self._state = TrackState.TRACKED
            else:
                if lost_count >= max_lost_frames:
                    self._state = TrackState.REMOVED
                else:
                    self._state = TrackState.LOST
            return self._state
