"""
VisionGuard Performance Telemetry View.
Satisfies Recommendation #6 (Metrics View reading from metrics collectors).
Renders real-time gauges and meters for FPS, CPU %, Memory MB, and Latencies.
"""

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QGridLayout, QGroupBox, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget
)
from visionguard.core.models import PerformanceMetrics


class TelemetryCard(QGroupBox):
    def __init__(self, title: str, unit: str = "", parent=None) -> None:
        super().__init__(title, parent)
        self.setStyleSheet(
            "QGroupBox { font-weight: bold; color: #00ffcc; border: 1px solid #2a2d3d; border-radius: 8px; font-size: 14px; background-color: #121318; }"
        )
        self.unit = unit
        layout = QVBoxLayout(self)
        self.val_label = QLabel("0.0")
        self.val_label.setAlignment(Qt.AlignCenter)
        self.val_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffffff;")
        layout.addWidget(self.val_label)

    def set_value(self, value: float) -> None:
        self.val_label.setText(f"{value:.1f} {self.unit}".strip())


class PerformanceView(QWidget):
    """Performance Monitoring View."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Hardware Telemetry & Execution Profiling")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffcc;")
        layout.addWidget(title)

        grid = QGridLayout()

        self.fps_card = TelemetryCard("Pipeline Throughput", "FPS")
        grid.addWidget(self.fps_card, 0, 0)

        self.cpu_card = TelemetryCard("CPU Utilization", "%")
        grid.addWidget(self.cpu_card, 0, 1)

        self.ram_card = TelemetryCard("Memory Footprint", "MB")
        grid.addWidget(self.ram_card, 0, 2)

        self.det_lat_card = TelemetryCard("Detection Latency", "ms")
        grid.addWidget(self.det_lat_card, 1, 0)

        self.track_lat_card = TelemetryCard("Tracking Latency", "ms")
        grid.addWidget(self.track_lat_card, 1, 1)

        self.total_lat_card = TelemetryCard("Total Frame Latency", "ms")
        grid.addWidget(self.total_lat_card, 1, 2)

        layout.addLayout(grid)
        layout.addStretch()

    @Slot(PerformanceMetrics)
    def update_metrics(self, metrics: PerformanceMetrics) -> None:
        self.fps_card.set_value(metrics.fps)
        self.cpu_card.set_value(metrics.cpu_usage_pct)
        self.ram_card.set_value(metrics.memory_mb)
        self.det_lat_card.set_value(metrics.detection_latency_ms)
        self.track_lat_card.set_value(metrics.tracking_latency_ms)
        self.total_lat_card.set_value(metrics.frame_processing_latency_ms)
