"""Latency profiler for execution timing."""
from collections import deque
import time
from typing import Dict

class LatencyProfiler:
    def __init__(self, window_size: int = 30) -> None:
        self.buffers: Dict[str, deque] = {}
        self.window_size = window_size

    def record(self, stage: str, latency_ms: float) -> None:
        if stage not in self.buffers:
            self.buffers[stage] = deque(maxlen=self.window_size)
        self.buffers[stage].append(latency_ms)

    def get_average(self, stage: str) -> float:
        if stage not in self.buffers or len(self.buffers[stage]) == 0:
            return 0.0
        return float(sum(self.buffers[stage]) / len(self.buffers[stage]))
