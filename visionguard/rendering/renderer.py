"""
VisionGuard Modular Annotation Renderer.
Satisfies Recommendation #7 (Separate Annotation Renderer). Provides clean, layer-based
OpenCV visual overlays (Regions, Trajectories, Bounding Boxes, Labels, OSD Telemetry).
"""

from typing import List, Optional
import cv2
import numpy as np
from visionguard.core.models import Detection, Event, FrameData, PerformanceMetrics, Region, RegionType, Track


class AnnotationRenderer:
    """Decoupled visual renderer for OpenCV frame annotations."""

    def __init__(
        self,
        show_boxes: bool = True,
        show_labels: bool = True,
        show_trajectories: bool = True,
        show_regions: bool = True,
        show_telemetry: bool = True,
    ) -> None:
        self.show_boxes = show_boxes
        self.show_labels = show_labels
        self.show_trajectories = show_trajectories
        self.show_regions = show_regions
        self.show_telemetry = show_telemetry

    def render(
        self,
        frame_data: FrameData,
        tracks: List[Track],
        regions: List[Region],
        active_events: Optional[List[Event]] = None,
        metrics: Optional[PerformanceMetrics] = None,
    ) -> np.ndarray:
        image = frame_data.image.copy()
        h, w = image.shape[:2]

        # Layer 1: Draw Regions & Counting Lines
        if self.show_regions and regions:
            self._draw_regions(image, regions)

        # Layer 2: Draw Motion Trajectories
        if self.show_trajectories and tracks:
            self._draw_trajectories(image, tracks)

        # Layer 3: Draw Bounding Boxes & Tracking IDs
        if self.show_boxes and tracks:
            self._draw_tracks(image, tracks)

        # Layer 4: Draw Active Event Banners
        if active_events:
            self._draw_event_alerts(image, active_events)

        # Layer 5: Draw Telemetry OSD Header
        if self.show_telemetry:
            self._draw_telemetry_osd(image, frame_data, metrics)

        return image

    def _draw_regions(self, image: np.ndarray, regions: List[Region]) -> None:
        overlay = image.copy()
        for r in regions:
            if not r.enabled:
                continue

            color = r.color

            if r.region_type in (RegionType.POLYGON, RegionType.ROI) and len(r.points) >= 3:
                pts = np.array(r.points, dtype=np.int32)
                cv2.polylines(image, [pts], isClosed=True, color=color, thickness=2)
                cv2.fillPoly(overlay, [pts], color=color)
                # Label
                cx, cy = int(np.mean([p[0] for p in r.points])), int(np.mean([p[1] for p in r.points]))
                cv2.putText(image, r.name, (cx - 40, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            elif r.region_type == RegionType.LINE and len(r.points) >= 2:
                p1 = (int(r.points[0][0]), int(r.points[0][1]))
                p2 = (int(r.points[1][0]), int(r.points[1][1]))
                cv2.line(image, p1, p2, color, 3)
                mid_x, mid_y = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
                cv2.putText(image, f"LINE: {r.name}", (mid_x - 30, mid_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Blend semi-transparent polygon fills
        cv2.addWeighted(overlay, 0.15, image, 0.85, 0, image)

    def _draw_trajectories(self, image: np.ndarray, tracks: List[Track]) -> None:
        for t in tracks:
            if len(t.trajectory) < 2:
                continue
            pts = np.array(t.trajectory, dtype=np.int32)
            cv2.polylines(image, [pts], isClosed=False, color=(0, 255, 255), thickness=2)

    def _draw_tracks(self, image: np.ndarray, tracks: List[Track]) -> None:
        for t in tracks:
            x1, y1, x2, y2 = int(t.x1), int(t.y1), int(t.x2), int(t.y2)

            # Color code based on track_id
            color_b = (t.track_id * 37) % 255
            color_g = (t.track_id * 67) % 255
            color_r = (t.track_id * 97) % 255
            bbox_color = (color_b, color_g, color_r)

            cv2.rectangle(image, (x1, y1), (x2, y2), bbox_color, 2)

            if self.show_labels:
                label = f"#{t.track_id} {t.class_name} {int(t.confidence * 100)}%"
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(image, (x1, y1 - 20), (x1 + w, y1), bbox_color, -1)
                cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def _draw_event_alerts(self, image: np.ndarray, events: List[Event]) -> None:
        for i, ev in enumerate(events):
            y_offset = 70 + (i * 30)
            text = f"ALERT: {ev.event_type.upper()} ({ev.object_class or 'Zone'})"
            cv2.rectangle(image, (15, y_offset - 20), (350, y_offset + 5), (0, 0, 220), -1)
            cv2.putText(image, text, (20, y_offset - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    def _draw_telemetry_osd(self, image: np.ndarray, frame_data: FrameData, metrics: Optional[PerformanceMetrics]) -> None:
        h, w = image.shape[:2]
        cv2.rectangle(image, (0, 0), (w, 35), (20, 20, 20), -1)

        fps_val = metrics.fps if metrics else frame_data.fps
        cpu_val = metrics.cpu_usage_pct if metrics else 0.0
        ram_val = metrics.memory_mb if metrics else 0.0

        osd_text = f"VisionGuard v1.0 | Cam: {frame_data.camera_id} | FPS: {fps_val:.1f} | CPU: {cpu_val}% | RAM: {ram_val:.0f}MB | Frame: {frame_data.frame_id}"
        cv2.putText(image, osd_text, (15, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 200), 1)
