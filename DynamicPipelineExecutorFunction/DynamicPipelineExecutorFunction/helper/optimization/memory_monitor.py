import os, psutil, gc


class MemoryMonitor:
    """Monitor and optimize memory usage."""

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.process = psutil.Process()

    def memory_critical(self) -> bool:
        """Check if memory usage is above threshold."""
        return psutil.virtual_memory().percent > (self.threshold * 100)

    def optimize_memory(self):
        """Perform memory optimization."""
        gc.collect()
        if hasattr(gc, "freeze"):  # CPython specific
            gc.freeze()
        if hasattr(os, "sync"):  # Unix specific
            os.sync()
