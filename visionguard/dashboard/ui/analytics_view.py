"""
VisionGuard Analytics View (Charts & Summaries).
Renders statistical charts for event distributions and object counts.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
)
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class AnalyticsView(QWidget):
    """Analytics View with Matplotlib statistical charts."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Spatial & Object Motion Analytics")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffcc;")
        layout.addWidget(title)

        # Matplotlib Figure
        self.figure = Figure(figsize=(8, 5), facecolor="#181a24")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self._render_charts()

    def _render_charts(self) -> None:
        self.figure.clear()
        
        # Subplot 1: Object Class Breakdown
        ax1 = self.figure.add_subplot(121)
        ax1.set_facecolor("#121318")
        classes = ["Person", "Car", "Truck", "Dog", "Backpack"]
        counts = [42, 18, 5, 8, 12]
        ax1.bar(classes, counts, color="#00ffcc")
        ax1.set_title("Detected Objects by Class", color="#ffffff", fontsize=12)
        ax1.tick_params(colors="#aaaaaa")
        ax1.spines['bottom'].set_color('#333333')
        ax1.spines['left'].set_color('#333333')

        # Subplot 2: Events Timeline Trend
        ax2 = self.figure.add_subplot(122)
        ax2.set_facecolor("#121318")
        time_points = [0, 5, 10, 15, 20, 25]
        events_cnt = [2, 4, 3, 7, 5, 9]
        ax2.plot(time_points, events_cnt, color="#ff0055", marker="o", linewidth=2)
        ax2.set_title("Events Triggered (Last 30 Min)", color="#ffffff", fontsize=12)
        ax2.tick_params(colors="#aaaaaa")
        ax2.spines['bottom'].set_color('#333333')
        ax2.spines['left'].set_color('#333333')

        self.figure.tight_layout()
        self.canvas.draw()
