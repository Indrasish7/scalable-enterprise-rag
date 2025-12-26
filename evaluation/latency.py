import time
from typing import Callable, Any


def measure_latency(func: Callable, *args, **kwargs) -> dict:
    """
    Measure execution latency of a function call.
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()

    return {
        "latency_ms": (end - start) * 1000,
        "result": result
    }
