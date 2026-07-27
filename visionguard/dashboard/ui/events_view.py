"""
VisionGuard Events View (Event Browser & Search).
Searchable table view displaying real-time triggered events.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)
from visionguard.core.models import Event


class EventsView(QWidget):
    """Events Browser and Filter Table View."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header Search Bar
        header = QHBoxLayout()
        title = QLabel("Security Event Log Browser")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffcc;")
        header.addWidget(title)

        header.addStretch()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter events by type, class, zone...")
        self.search_box.setStyleSheet("background-color: #1a1c26; color: #ffffff; padding: 6px 12px; border-radius: 6px;")
        header.addWidget(self.search_box)

        layout.addLayout(header)

        # Events Table Widget
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "Camera ID", "Event Type", "Severity", "Object Class", "Zone", "Snapshot"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(
            "QTableWidget { background-color: #121318; gridline-color: #2a2d3d; color: #e0e0e0; }"
            "QHeaderView::section { background-color: #1a1c26; color: #00ffcc; font-weight: bold; padding: 6px; }"
        )
        layout.addWidget(self.table)

    def add_event(self, event: Event) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)

        time_str = event.timestamp
        self.table.setItem(row, 0, QTableWidgetItem(str(round(time_str, 2))))
        self.table.setItem(row, 1, QTableWidgetItem(event.camera_id))
        self.table.setItem(row, 2, QTableWidgetItem(event.event_type))
        self.table.setItem(row, 3, QTableWidgetItem(event.severity.value.upper()))
        self.table.setItem(row, 4, QTableWidgetItem(event.object_class or "N/A"))
        self.table.setItem(row, 5, QTableWidgetItem(event.zone_name or "Global"))
        self.table.setItem(row, 6, QTableWidgetItem(event.snapshot_path or "None"))
