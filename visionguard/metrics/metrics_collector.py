"""
Centralized Metrics Collector unifying CPU, Memory, FPS, and Latency into PerformanceMetrics objects.
"""

from collections import deque
from typing import List
from visionguard.core.models import PerformanceMetrics
from visionguard.metrics.cpu import CpuCollector
from visionguard.metrics.fps import FpsCalculator
from visionguard.metrics.latency import LatencyProfiler
from visionguard.metrics.memory import MemoryCollector


class MetricsCollector:
    """Aggregates system telemetry and processing performance metrics."""
    def __init__(self, history_buffer_size: int = 100) -> None:
        self.fps_calc = FpsCalculator()
        self.latency_profiler = LatencyProfiler()
        self.history: deque[PerformanceMetrics] = deque(maxlen=history_buffer_size)
        self.drop_count: int = 0

    def tick_frame(self) -> None:
        self.fps_calc.tick()

    def record_latency(self, stage: str, latency_ms: float) -> None:
        self.latency_profiler.record(stage, latency_ms)

    def record_frame_drop(self) -> None:
        self.drop_count += 1

    def collect(self) -> PerformanceMetrics:
        metrics = PerformanceMetrics(
            fps=round(self.fps_calc.get_fps(), 2),
            frame_processing_latency_ms=round(self.latency_profiler.get_average("pipeline"), 2),
            detection_latency_ms=round(self.latency_profiler.get_average("detection"), 2),
            tracking_latency_ms=round(self.latency_profiler.get_average("tracking"), 2),
            cpu_usage_pct=round(CpuCollector.get_cpu_percent(), 1),
            memory_mb=round(MemoryCollector.get_process_memory_mb(), 1),
            frame_drop_count=self.drop_count,
        )
        self.history.append(metrics)
        return metrics

    def get_history(self) -> List[PerformanceMetrics]:
        return list(self.history)
