"""
VisionGuard Home View (Live Video Feed & Stream Status).
Renders real-time annotated video frames on PySide6 QLabel widgets.
"""

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget
)
from visionguard.core.models import FrameData


class LiveVideoWidget(QLabel):
    """Widget displaying OpenCV video frames as Qt Pixmaps."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(640, 360)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #121318; border: 2px solid #2a2d3d; border-radius: 8px;")
        self.setText("Awaiting Video Stream...")

    @Slot(np.ndarray)
    def update_frame(self, image: np.ndarray) -> None:
        if image is None:
            return

        h, w, ch = image.shape
        rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        bytes_per_line = ch * w
        q_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled_pixmap)


class HomeView(QWidget):
    """Main Home Dashboard View."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header Status Bar
        header_layout = QHBoxLayout()
        title_label = QLabel("Live Video Analytics Feed")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffcc;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.cam_status_badge = QLabel("● STREAMING")
        self.cam_status_badge.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #00ffaa; background-color: #1a332a; padding: 6px 12px; border-radius: 12px;"
        )
        header_layout.addWidget(self.cam_status_badge)

        layout.addLayout(header_layout)

        # Video Display Frame
        self.video_display = LiveVideoWidget(self)
        layout.addWidget(self.video_display)

    def display_frame(self, frame_data: FrameData) -> None:
        img = frame_data.annotated_image if frame_data.annotated_image is not None else frame_data.image
        self.video_display.update_frame(img)
