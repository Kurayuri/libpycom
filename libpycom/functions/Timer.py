import time

class Timer:
    def __init__(self, text="Elapsed time:"):
        self.text = text
        self._elapsed_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self._elapsed_time = self.end_time - self.start_time
        print(f"{self.text} {self._elapsed_time:.2f}s")
        return False

    @property
    def elapsed_time(self):
        return self._elapsed_time
