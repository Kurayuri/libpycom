import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Optional, List, Tuple, Callable


class WallTimeProfilerStopwatch:
    def __init__(self, profiler, name: str):
        self.profiler = profiler
        self.name = name
        self.stime = None
    
    def start(self):
        self.stime = time.perf_counter()
        return self
    
    def stop(self):
        if self.stime is None:
            raise RuntimeError("Stopwatch was not started.")
        etime = time.perf_counter()
        duration = etime - self.stime
        with self.profiler._lock:
            self.profiler._stats[self.name][0] += duration
            self.profiler._stats[self.name][1] += 1
        self.stime = None
        return self

class WallTimeProfiler:
    """
    A lightweight, thread-safe wall-time profiler that mimics the interface of
    torch.profiler.record_function. It measures CPU wall-clock time (not GPU time).
    
    Usage:
        profiler = WallTimeProfiler()
        with profiler.record_function("forward"):
            model(x)
        print(profiler.key_averages().table(sort_by="time_total", row_limit=10))

        # Or as a decorator:
        @profiler.profile
        def my_func():
            ...

        # Or with custom name:
        @profiler.profile("custom_name")
        def another_func():
            ...
    """

    def __init__(self):
        self._lock = threading.Lock()
        # stats: {name: [total_time_sec, call_count]}
        self._stats = defaultdict(lambda: [0.0, 0])
        self._stopwatches = {}
        # Thread-local stack for debugging or future hierarchical profiling
        self._local = threading.local()

    @contextmanager
    def record_function(self, name: str):
        """
        Context manager to profile a named code region.
        
        Args:
            name (str): Name of the operation to profile.
        """
        start = time.perf_counter()
        try:
            if not hasattr(self._local, 'stack'):
                self._local.stack = []
            self._local.stack.append(name)
            yield
        finally:
            end = time.perf_counter()
            duration = end - start

            with self._lock:
                self._stats[name][0] += duration
                self._stats[name][1] += 1

            if self._local.stack:
                self._local.stack.pop()
    


    def stopwatch(self, name: str):
        return self._stopwatches.setdefault(name, WallTimeProfilerStopwatch(self, name))

    def profile(self, name_or_func=None):
        """
        Decorator to profile a function.
        
        Can be used in two ways:
        
        1. @profiler.profile
           def func(): ...
           -> uses func.__qualname__ as name

        2. @profiler.profile("custom_name")
           def func(): ...
           -> uses "custom_name"
        """
        if callable(name_or_func):
            # Case 1: @profiler.profile (no parentheses)
            func = name_or_func
            name = func.__qualname__
            return self._make_wrapper(func, name)
        else:
            # Case 2: @profiler.profile("name") or @profiler.profile()
            name = name_or_func  # could be None, but we'll handle it

            def decorator(func: Callable) -> Callable:
                nonlocal name
                if name is None:
                    name = func.__qualname__
                return self._make_wrapper(func, name)
            return decorator

    def _make_wrapper(self, func: Callable, name: str) -> Callable:
        """Create a wrapped function that profiles using record_function."""
        def wrapper(*args, **kwargs):
            with self.record_function(name):
                return func(*args, **kwargs)
        # Preserve metadata (optional but good practice)
        wrapper.__name__ = func.__name__
        wrapper.__qualname__ = func.__qualname__
        wrapper.__doc__ = func.__doc__
        return wrapper

    def key_averages(self):
        """Returns self for fluent interface (matches torch.profiler API)."""
        return self

    def profile_iterator(self, iterable, name: str):
        """
        Wraps an iterable so that each element's generation (i.e., each __next__ call)
        is profiled under the given name.

        Usage:
            profiler = WallTimeProfiler()
            for batch in profiler.profile_iterator(dataloader, "data_loading"):
                # process batch
                pass

        This measures the time spent in dataloader.__next__() (or equivalent),
        excluding the loop body.
        """
        iterator = iter(iterable)
        while True:
            try:
                with self.record_function(name):
                    item = next(iterator)
                yield item
            except StopIteration:
                break


    def table(
        self,
        sort_by: Optional[str] = "time_total",
        row_limit: Optional[int] = None,
        max_name_column_width: int = 50
    ) -> str:
        """
        Returns a formatted string summarizing profiling results.
        """
        if not self._stats:
            return "No profiling data collected."

        sort_key_map = {
            "time_total": lambda x: x[1][0],
            "calls": lambda x: x[1][1],
            "time_avg": lambda x: x[1][0] / x[1][1] if x[1][1] > 0 else 0,
        }
        if sort_by not in sort_key_map:
            raise ValueError(f"Unsupported sort_by: {sort_by}. "
                             f"Choose from {list(sort_key_map.keys())}")

        items: List[Tuple[str, List[float]]] = list(self._stats.items())
        items.sort(key=sort_key_map[sort_by], reverse=True)

        if row_limit is not None:
            items = items[:row_limit]

        lines = []
        header = f"{'Name':<{max_name_column_width}} {'Total Time (s)':<16} {'Calls':<8} {'Avg (ms)':<10}"
        lines.append("-" * len(header))
        lines.append(header)
        lines.append("-" * len(header))

        for name, (total_time, calls) in items:
            disp_name = (name[:max_name_column_width - 3] + "...") if len(name) > max_name_column_width else name
            avg_ms = (total_time / calls) * 1000.0 if calls > 0 else 0.0
            line = f"{disp_name:<{max_name_column_width}} {total_time:<16.6f} {int(calls):<8} {avg_ms:<10.3f}"
            lines.append(line)

        lines.append("-" * len(header))
        return "\n".join(lines)

    def reset(self):
        """Clear all collected profiling data."""
        with self._lock:
            self._stats.clear()
