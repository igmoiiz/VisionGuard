"""
VisionGuard Settings View (Camera & Threshold Configurator).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QSlider, QVBoxLayout, QWidget
)


class SettingsView(QWidget):
    """Interactive Settings and Detection Threshold View."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("System Configuration & Detection Settings")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffcc;")
        layout.addWidget(title)

        # Form layout
        group = QGroupBox("YOLO Detection & CPU Optimization Controls")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #ffffff; border: 1px solid #2a2d3d; margin-top: 10px; }")
        form = QFormLayout(group)

        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(10, 95)
        self.conf_slider.setValue(35)
        form.addRow("Confidence Threshold (%):", self.conf_slider)

        self.iou_slider = QSlider(Qt.Horizontal)
        self.iou_slider.setRange(10, 95)
        self.iou_slider.setValue(45)
        form.addRow("IoU NMS Threshold (%):", self.iou_slider)

        self.skip_slider = QSlider(Qt.Horizontal)
        self.skip_slider.setRange(1, 5)
        self.skip_slider.setValue(1)
        form.addRow("Frame Skip (Process Every N Frames):", self.skip_slider)

        layout.addWidget(group)
        layout.addStretch()
