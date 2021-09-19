import time


class Timer:
    start: float
    end: float

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end = time.time()

    @property
    def elapsed(self) -> int:
        return int(self.end - self.start)
