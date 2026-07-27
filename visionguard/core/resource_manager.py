"""
VisionGuard Resource Manager.
Centralized manager responsible for managing system lifecycle, thread pools,
shared queues, background worker tasks, and graceful shutdown handling.
"""

from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import signal
import sys
from threading import Event as ThreadEvent, Lock
from typing import Any, Dict, Optional
from visionguard.logging.logger import logger


class ResourceManager:
    """Centralized lifecycle & resource manager for VisionGuard."""
    _instance: Optional["ResourceManager"] = None

    def __init__(self, max_workers: int = 8) -> None:
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="vg_worker")
        self.shutdown_event = ThreadEvent()
        self.queues: Dict[str, Queue] = {}
        self.services: Dict[str, Any] = {}
        self._lock = Lock()
        self._setup_signal_handlers()

    @classmethod
    def get_instance(cls) -> "ResourceManager":
        if cls._instance is None:
            cls._instance = ResourceManager()
        return cls._instance

    def _setup_signal_handlers(self) -> None:
        try:
            signal.signal(signal.SIGINT, self._handle_shutdown_signal)
            signal.signal(signal.SIGTERM, self._handle_shutdown_signal)
        except Exception:
            pass  # May be skipped if running in non-main thread

    def _handle_shutdown_signal(self, signum, frame) -> None:
        logger.warning(f"Received termination signal ({signum}). Initiating graceful shutdown...")
        self.shutdown()

    def get_queue(self, name: str, maxsize: int = 100) -> Queue:
        with self._lock:
            if name not in self.queues:
                self.queues[name] = Queue(maxsize=maxsize)
            return self.queues[name]

    def register_service(self, name: str, service_obj: Any) -> None:
        with self._lock:
            self.services[name] = service_obj
            logger.info(f"Registered service: '{name}'")

    def get_service(self, name: str) -> Optional[Any]:
        with self._lock:
            return self.services.get(name)

    def is_shutting_down(self) -> bool:
        return self.shutdown_event.is_set()

    def shutdown(self) -> None:
        if self.shutdown_event.is_set():
            return

        logger.info("ResourceManager: Shutting down all services and thread pools...")
        self.shutdown_event.set()

        # Stop services that implement a stop() method
        with self._lock:
            for name, service in self.services.items():
                if hasattr(service, "stop") and callable(service.stop):
                    try:
                        logger.info(f"Stopping service '{name}'...")
                        service.stop()
                    except Exception as e:
                        logger.error(f"Error stopping service '{name}': {e}")

        # Shutdown thread pool
        self.thread_pool.shutdown(wait=False, cancel_futures=True)
        logger.info("ResourceManager: Cleanup completed successfully.")
