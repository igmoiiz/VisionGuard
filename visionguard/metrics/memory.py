"""RAM memory collector using psutil."""
import os
import psutil

class MemoryCollector:
    @staticmethod
    def get_process_memory_mb() -> float:
        try:
            process = psutil.Process(os.getpid())
            return float(process.memory_info().rss / (1024 * 1024))
        except Exception:
            return 0.0

    @staticmethod
    def get_system_memory_percent() -> float:
        try:
            return float(psutil.virtual_memory().percent)
        except Exception:
            return 0.0
