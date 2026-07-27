"""System Health and Status API routes."""
import time
from fastapi import APIRouter
from visionguard.metrics.cpu import CpuCollector
from visionguard.metrics.memory import MemoryCollector

router = APIRouter(prefix="/api/v1/system", tags=["System"])

START_TIME = time.time()

@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": "VisionGuard Analytics Engine",
        "uptime_seconds": round(time.time() - START_TIME, 1),
    }

@router.get("/status")
def get_status():
    return {
        "cpu_usage_pct": CpuCollector.get_cpu_percent(),
        "memory_mb": MemoryCollector.get_process_memory_mb(),
        "system_ram_pct": MemoryCollector.get_system_memory_percent(),
        "cpu_cores": CpuCollector.get_cpu_count(),
    }
