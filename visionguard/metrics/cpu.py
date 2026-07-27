"""CPU usage collector using psutil."""
import psutil

class CpuCollector:
    @staticmethod
    def get_cpu_percent() -> float:
        try:
            return float(psutil.cpu_percent(interval=None))
        except Exception:
            return 0.0

    @staticmethod
    def get_cpu_count() -> int:
        try:
            return psutil.cpu_count(logical=True) or 1
        except Exception:
            return 1
