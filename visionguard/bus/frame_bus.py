"""
VisionGuard Asynchronous Frame & Event Bus.
Implements a high-performance Publish/Subscribe message bus decoupling video ingestion,
AI inference, tracking, event processing, video recording, and UI/API streaming.
"""

from collections import defaultdict
from queue import Full, Queue
from threading import Lock, Thread
from typing import Any, Callable, Dict, List
from visionguard.logging.logger import logger


class FrameBus:
    """Thread-safe Pub/Sub message bus for real-time video frames and system events."""

    def __init__(self, queue_maxsize: int = 30) -> None:
        self._subscribers: Dict[str, List[Queue]] = defaultdict(list)
        self._callbacks: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
        self._queue_maxsize = queue_maxsize
        self._lock = Lock()

    def subscribe_queue(self, topic: str) -> Queue:
        """Subscribes an asynchronous Queue to a topic."""
        q: Queue = Queue(maxsize=self._queue_maxsize)
        with self._lock:
            self._subscribers[topic].append(q)
            logger.debug(f"FrameBus: Queue subscribed to topic '{topic}'")
        return q

    def unsubscribe_queue(self, topic: str, q: Queue) -> None:
        """Unsubscribes a Queue from a topic."""
        with self._lock:
            if q in self._subscribers[topic]:
                self._subscribers[topic].remove(q)
                logger.debug(f"FrameBus: Queue unsubscribed from topic '{topic}'")

    def subscribe_callback(self, topic: str, callback: Callable[[Any], None]) -> None:
        """Subscribes a synchronous callback function to a topic."""
        with self._lock:
            if callback not in self._callbacks[topic]:
                self._callbacks[topic].append(callback)
                logger.debug(f"FrameBus: Callback subscribed to topic '{topic}'")

    def unsubscribe_callback(self, topic: str, callback: Callable[[Any], None]) -> None:
        """Unsubscribes a callback from a topic."""
        with self._lock:
            if callback in self._callbacks[topic]:
                self._callbacks[topic].remove(callback)

    def publish(self, topic: str, payload: Any) -> None:
        """Publishes a payload to all topic subscribers."""
        with self._lock:
            queues = list(self._subscribers[topic])
            callbacks = list(self._callbacks[topic])

        # Non-blocking queue publish (drop frame if consumer queue is full to maintain real-time FPS)
        for q in queues:
            try:
                q.put_nowait(payload)
            except Full:
                pass  # Drop payload to prevent latency accumulation

        # Execute callbacks
        for cb in callbacks:
            try:
                cb(payload)
            except Exception as e:
                logger.error(f"FrameBus: Error executing callback for topic '{topic}': {e}")
