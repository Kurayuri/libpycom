import time
from types import EllipsisType


class Stopwatch:
    def __init__(self, text="Elapsed time:", precision: int | EllipsisType = 2):
        self.text = text
        self.precision = precision
        self._elapsed_time = None

    def __enter__(self):
        # self.start_time = time.time()
        self.start_time = time.perf_counter_ns()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # self.end_time = time.time()
        # self._elapsed_time = self.end_time - self.start_time
        self.end_time = time.perf_counter_ns()
        self._elapsed_time = (self.end_time - self.start_time) / 1_000_000_000
        if isinstance(self.precision, int):
            print(f"{self.text} {self._elapsed_time:.{self.precision}f}s")
        else:
            print(f"{self.text} {self._elapsed_time}s")

        return False

    @property
    def elapsed_time(self):
        return self._elapsed_time
