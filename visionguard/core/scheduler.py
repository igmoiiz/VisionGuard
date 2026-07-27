"""
VisionGuard Task Scheduler.
Runs background maintenance jobs on configurable intervals (e.g. video retention cleanup,
database WAL checkpointing, and performance metrics archiving).
"""

from pathlib import Path
import time
from threading import Thread
from typing import Callable, List, Tuple
from visionguard.logging.logger import logger


class TaskScheduler:
    """Lightweight background task scheduler."""
    def __init__(self) -> None:
        self.tasks: List[Tuple[str, Callable[[], None], float, float]] = []  # (name, func, interval_sec, last_run)
        self.running = False
        self._thread: Thread = None

    def add_task(self, name: str, func: Callable[[], None], interval_sec: float) -> None:
        self.tasks.append((name, func, interval_sec, 0.0))
        logger.info(f"TaskScheduler: Registered task '{name}' (Interval: {interval_sec}s)")

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._thread = Thread(target=self._run_loop, daemon=True, name="vg_scheduler")
        self._thread.start()
        logger.info("TaskScheduler started")

    def stop(self) -> None:
        self.running = False

    def _run_loop(self) -> None:
        while self.running:
            now = time.time()
            for i, (name, func, interval, last_run) in enumerate(self.tasks):
                if now - last_run >= interval:
                    try:
                        func()
                    except Exception as e:
                        logger.error(f"TaskScheduler: Exception executing '{name}': {e}")
                    self.tasks[i] = (name, func, interval, now)
            time.sleep(1.0)


def create_default_scheduler(recordings_dir: str = "data/recordings", retention_days: int = 7) -> TaskScheduler:
    """Helper to initialize standard background cleanup tasks."""
    scheduler = TaskScheduler()

    def cleanup_old_recordings():
        recordings_path = Path(recordings_dir)
        if not recordings_path.exists():
            return
        cutoff_time = time.time() - (retention_days * 86400)
        cleaned_count = 0
        for item in recordings_path.glob("*.*"):
            if item.is_file() and item.stat().st_mtime < cutoff_time:
                try:
                    item.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete old file {item}: {e}")
        if cleaned_count > 0:
            logger.info(f"TaskScheduler Retention Cleanup: Deleted {cleaned_count} old file(s).")

    # Schedule cleanup every hour
    scheduler.add_task("retention_cleanup", cleanup_old_recordings, interval_sec=3600.0)
    return scheduler
