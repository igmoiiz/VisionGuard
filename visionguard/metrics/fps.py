"""Real-time FPS calculator using sliding window timing."""
from collections import deque
import time

class FpsCalculator:
    def __init__(self, window_size: int = 30) -> None:
        self.timestamps = deque(maxlen=window_size)

    def tick(self) -> None:
        self.timestamps.append(time.time())

    def get_fps(self) -> float:
        if len(self.timestamps) < 2:
            return 0.0
        elapsed = self.timestamps[-1] - self.timestamps[0]
        if elapsed <= 0:
            return 0.0
        return float((len(self.timestamps) - 1) / elapsed)
