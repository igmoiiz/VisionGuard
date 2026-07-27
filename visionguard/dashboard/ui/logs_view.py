"""
VisionGuard Live Application Log Viewer.
Streams Loguru logs directly into a PySide6 QTextEdit widget.
"""

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget
from visionguard.logging.logger import log_stream_handler


class LogsView(QWidget):
    """Live Log Viewer Widget."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._init_ui()
        log_stream_handler.subscribe(self.append_log)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("System Application Logs")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffcc;")
        layout.addWidget(title)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet(
            "QTextEdit { background-color: #0b0c10; color: #00ffaa; font-family: monospace; font-size: 12px; border: 1px solid #2a2d3d; }"
        )
        layout.addWidget(self.text_edit)

    @Slot(str)
    def append_log(self, text: str) -> None:
        self.text_edit.append(text.strip())
