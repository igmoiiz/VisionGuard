"""
VisionGuard Logging System.
Configures Loguru for high-performance structured logging, file rotation,
console coloring via Rich, and in-memory log streaming for GUI/API subscribers.
"""

import sys
from pathlib import Path
from typing import Callable, List
from loguru import logger


class LogStreamHandler:
    """Thread-safe log handler to stream logs to registered callbacks (GUI / WebSockets)."""
    def __init__(self) -> None:
        self.subscribers: List[Callable[[str], None]] = []

    def subscribe(self, callback: Callable[[str], None]) -> None:
        if callback not in self.subscribers:
            self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[str], None]) -> None:
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def emit(self, message) -> None:
        formatted = str(message)
        for subscriber in self.subscribers:
            try:
                subscriber(formatted)
            except Exception:
                pass


log_stream_handler = LogStreamHandler()


def setup_logger(log_dir: str = "data/logs", level: str = "INFO") -> None:
    """
    Initializes Loguru sinks:
    1. Standard error / terminal sink with color formatting.
    2. Daily rotating log file sink with JSON formatting support.
    3. Custom stream sink for GUI and WebSocket clients.
    """
    logger.remove()  # Remove default handler

    # Console sink
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
        enqueue=True,
    )

    # File sink
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    file_path = Path(log_dir) / "visionguard_{time:YYYY-MM-DD}.log"
    logger.add(
        str(file_path),
        rotation="10 MB",
        retention="7 days",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
        enqueue=True,
        encoding="utf-8",
    )

    # Custom stream sink for UI / API subscriber broadcast
    logger.add(
        log_stream_handler.emit,
        level=level,
        format="{time:HH:mm:ss} [{level}] {message}",
        enqueue=True,
    )

    logger.info("VisionGuard Logging System Initialized")
