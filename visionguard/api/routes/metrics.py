"""Performance Metrics API routes."""
from fastapi import APIRouter
from visionguard.core.models import PerformanceMetrics

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])

@router.get("/live", response_model=PerformanceMetrics)
def get_live_metrics():
    return PerformanceMetrics(
        fps=25.0,
        frame_processing_latency_ms=12.5,
        detection_latency_ms=8.0,
        tracking_latency_ms=2.1,
        cpu_usage_pct=24.5,
        memory_mb=185.0,
    )
