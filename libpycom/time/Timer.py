import time
from types import EllipsisType


class Timer:
    def __init__(self, text="Elapsed time:", precision: int | EllipsisType = 2):
        self.text = text
        self.precision = precision
        self._elapsed_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self._elapsed_time = self.end_time - self.start_time
        if isinstance(self.precision, int):
            print(f"{self.text} {self._elapsed_time:.{self.precision}f}s")
        else:
            print(f"{self.text} {self._elapsed_time}s")

        return False

    @property
    def elapsed_time(self):
        return self._elapsed_time
