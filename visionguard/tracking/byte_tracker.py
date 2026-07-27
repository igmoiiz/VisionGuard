"""
VisionGuard ByteTrack Multi-Object Tracker.
Implements the ByteTrack tracking algorithm associating both high-confidence and low-confidence
detection bounding boxes using Kalman filtering / IoU linear assignment.
"""

from collections import deque
from datetime import datetime
import time
from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import linear_sum_assignment
from visionguard.core.models import Detection, Track, TrackState
from visionguard.logging.logger import logger
from visionguard.tracking.base_tracker import BaseTracker


def compute_iou(box1: Tuple[float, float, float, float], box2: Tuple[float, float, float, float]) -> float:
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union = area1 + area2 - intersection
    if union <= 0:
        return 0.0
    return float(intersection / union)


class STrack:
    """Internal ByteTrack Single Tracklet object."""
    _count = 0

    def __init__(self, detection: Detection, max_trajectory_len: int = 50) -> None:
        STrack._count += 1
        self.track_id = STrack._count
        self.bbox = detection.bbox
        self.class_id = detection.class_id
        self.class_name = detection.class_name
        self.confidence = detection.confidence
        self.trajectory = deque(maxlen=max_trajectory_len)
        self.state = TrackState.NEW
        self.age = 1
        self.time_since_update = 0
        self.first_seen_timestamp = time.time()
        self.last_seen_timestamp = time.time()
        self.stationary_duration_sec = 0.0

        centroid = ((self.bbox[0] + self.bbox[2]) / 2.0, (self.bbox[1] + self.bbox[3]) / 2.0)
        self.trajectory.append(centroid)

    @property
    def centroid(self) -> Tuple[float, float]:
        return self.trajectory[-1] if self.trajectory else ((self.bbox[0] + self.bbox[2]) / 2.0, (self.bbox[1] + self.bbox[3]) / 2.0)

    @property
    def velocity(self) -> Tuple[float, float]:
        if len(self.trajectory) < 2:
            return (0.0, 0.0)
        p1 = self.trajectory[-2]
        p2 = self.trajectory[-1]
        return (p2[0] - p1[0], p2[1] - p1[1])

    def update(self, detection: Detection) -> None:
        self.bbox = detection.bbox
        self.confidence = detection.confidence
        self.age += 1
        self.time_since_update = 0
        self.state = TrackState.TRACKED
        self.last_seen_timestamp = time.time()

        new_centroid = ((self.bbox[0] + self.bbox[2]) / 2.0, (self.bbox[1] + self.bbox[3]) / 2.0)
        
        # Calculate movement distance for stationary tracking
        if self.trajectory:
            prev_centroid = self.trajectory[-1]
            dist = float(np.hypot(new_centroid[0] - prev_centroid[0], new_centroid[1] - prev_centroid[1]))
            if dist < 3.0:  # Threshold for minimal movement
                self.stationary_duration_sec += 0.04  # ~25 fps increment
            else:
                self.stationary_duration_sec = 0.0

        self.trajectory.append(new_centroid)

    def mark_lost(a) -> None:
        self.time_since_update += 1
        self.state = TrackState.LOST

    def to_track_model(self) -> Track:
        return Track(
            track_id=self.track_id,
            class_id=self.class_id,
            class_name=self.class_name,
            confidence=self.confidence,
            bbox=self.bbox,
            centroid=self.centroid,
            trajectory=list(self.trajectory),
            velocity=self.velocity,
            state=self.state,
            age=self.age,
            time_since_update=self.time_since_update,
            stationary_duration_sec=self.stationary_duration_sec,
            first_seen_timestamp=self.first_seen_timestamp,
            last_seen_timestamp=self.last_seen_timestamp,
        )


class ByteTrackerPlugin(BaseTracker):
    """ByteTrack Multi-Object Tracker Plugin."""

    def __init__(
        self,
        track_high_thresh: float = 0.5,
        track_low_thresh: float = 0.1,
        new_track_thresh: float = 0.6,
        match_thresh: float = 0.8,
        track_buffer: int = 30,
        max_trajectory_length: int = 50,
    ) -> None:
        self.track_high_thresh = track_high_thresh
        self.track_low_thresh = track_low_thresh
        self.new_track_thresh = new_track_thresh
        self.match_thresh = match_thresh
        self.track_buffer = track_buffer
        self.max_trajectory_length = max_trajectory_length

        self.tracked_stracks: List[STrack] = []
        self.lost_stracks: List[STrack] = []

    def reset(self) -> None:
        self.tracked_stracks.clear()
        self.lost_stracks.clear()
        STrack._count = 0

    def update(self, detections: List[Detection], image: np.ndarray) -> List[Track]:
        high_dets: List[Detection] = []
        low_dets: List[Detection] = []

        for det in detections:
            if det.confidence >= self.track_high_thresh:
                high_dets.append(det)
            elif det.confidence >= self.track_low_thresh:
                low_dets.append(det)

        # 1st association with high-confidence detections
        unmatched_stracks, matched_dets = self._associate(self.tracked_stracks, high_dets, self.match_thresh)

        # 2nd association: unmatched tracks with low-confidence detections
        second_unmatched, _ = self._associate(unmatched_stracks, low_dets, 0.5)

        # Mark remaining unmatched as lost
        for strack in second_unmatched:
            strack.mark_lost()
            if strack not in self.lost_stracks:
                self.lost_stracks.append(strack)
            if strack in self.tracked_stracks:
                self.tracked_stracks.remove(strack)

        # Create new tracks for unmatched high confidence detections
        unmatched_high = [det for i, det in enumerate(high_dets) if i not in matched_dets]
        for det in unmatched_high:
            if det.confidence >= self.new_track_thresh:
                new_strack = STrack(det, max_trajectory_len=self.max_trajectory_length)
                new_strack.state = TrackState.TRACKED
                self.tracked_stracks.append(new_strack)

        # Remove dead tracks that exceeded track_buffer
        self.lost_stracks = [st for st in self.lost_stracks if st.time_since_update <= self.track_buffer]

        active_tracks = [st.to_track_model() for st in self.tracked_stracks if st.state == TrackState.TRACKED]
        return active_tracks

    def _associate(self, stracks: List[STrack], detections: List[Detection], thresh: float) -> Tuple[List[STrack], List[int]]:
        if not stracks or not detections:
            return stracks, []

        cost_matrix = np.zeros((len(stracks), len(detections)), dtype=np.float32)
        for i, st in enumerate(stracks):
            for j, det in enumerate(detections):
                cost_matrix[i, j] = 1.0 - compute_iou(st.bbox, det.bbox)

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        unmatched_stracks: List[STrack] = []
        matched_dets: List[int] = []

        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r, c] < (1.0 - thresh):
                stracks[r].update(detections[c])
                matched_dets.append(c)
            else:
                unmatched_stracks.append(stracks[r])

        for i, st in enumerate(stracks):
            if i not in row_ind:
                unmatched_stracks.append(st)

        return unmatched_stracks, matched_dets
