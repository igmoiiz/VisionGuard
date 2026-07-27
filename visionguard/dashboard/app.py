"""
VisionGuard PySide6 Main Dashboard Application Window.
Provides dark-mode desktop GUI hosting 6 specialized views, navigation sidebars,
and real-time FrameBus subscriber integrations.
"""

from typing import Optional
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QStackedWidget, QVBoxLayout, QWidget
)
from visionguard.bus.frame_bus import FrameBus
from visionguard.core.models import Event, FrameData, PerformanceMetrics
from visionguard.dashboard.ui.analytics_view import AnalyticsView
from visionguard.dashboard.ui.events_view import EventsView
from visionguard.dashboard.ui.home_view import HomeView
from visionguard.dashboard.ui.logs_view import LogsView
from visionguard.dashboard.ui.performance_view import PerformanceView
from visionguard.dashboard.ui.settings_view import SettingsView
from visionguard.logging.logger import logger


class MainWindow(QMainWindow):
    """Main Application Window with Sidebar Navigation."""

    def __init__(self, frame_bus: Optional[FrameBus] = None) -> None:
        super().__init__()
        self.frame_bus = frame_bus
        self.setWindowTitle("VisionGuard — Intelligent Video Analytics Platform")
        self.resize(1360, 768)

        self._apply_theme()
        self._init_ui()
        self._setup_bus_subscriptions()

    def _apply_theme(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background-color: #0b0c10; color: #ffffff; }
            QWidget { background-color: #0b0c10; color: #e0e0e0; font-family: 'Segoe UI', Arial, sans-serif; }
            QListWidget { background-color: #121318; border: none; border-right: 1px solid #1f222e; }
            QListWidget::item { padding: 12px 20px; color: #aaaaaa; font-size: 14px; font-weight: 500; border-left: 3px solid transparent; }
            QListWidget::item:hover { background-color: #181a24; color: #ffffff; }
            QListWidget::item:selected { background-color: #1a2234; color: #00ffcc; border-left: 3px solid #00ffcc; font-weight: bold; }
        """)

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar Navigation
        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        logo_label = QLabel(" VisionGuard")
        logo_label.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #00ffcc; padding: 20px; background-color: #121318;"
        )
        sidebar_layout.addWidget(logo_label)

        self.nav_list = QListWidget()
        self.nav_list.addItem("🏠 Home Feed")
        self.nav_list.addItem("📊 Analytics")
        self.nav_list.addItem("🚨 Events Log")
        self.nav_list.addItem("⚙️ Settings")
        self.nav_list.addItem("⚡ Performance")
        self.nav_list.addItem("📋 Live Logs")
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        sidebar_layout.addWidget(self.nav_list)

        main_layout.addWidget(sidebar_container)

        # Main Content Stacked Widget
        self.stack = QStackedWidget()

        self.home_view = HomeView()
        self.analytics_view = AnalyticsView()
        self.events_view = EventsView()
        self.settings_view = SettingsView()
        self.performance_view = PerformanceView()
        self.logs_view = LogsView()

        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.analytics_view)
        self.stack.addWidget(self.events_view)
        self.stack.addWidget(self.settings_view)
        self.stack.addWidget(self.performance_view)
        self.stack.addWidget(self.logs_view)

        main_layout.addWidget(self.stack)

    def _on_nav_changed(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

    def _setup_bus_subscriptions(self) -> None:
        if self.frame_bus:
            self.frame_bus.subscribe_callback("frames", self._on_frame_received)
            self.frame_bus.subscribe_callback("events", self._on_event_received)
            self.frame_bus.subscribe_callback("metrics", self._on_metrics_received)

    def _on_frame_received(self, frame_data: FrameData) -> None:
        self.home_view.display_frame(frame_data)

    def _on_event_received(self, event: Event) -> None:
        self.events_view.add_event(event)

    def _on_metrics_received(self, metrics: PerformanceMetrics) -> None:
        self.performance_view.update_metrics(metrics)


def launch_dashboard(frame_bus: Optional[FrameBus] = None) -> None:
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MainWindow(frame_bus=frame_bus)
    window.show()
    sys.exit(app.exec())
