from typing import Callable, Iterable, Any
from rich.progress import Progress
from enum import IntEnum
from libpycom.Const import LEVEL, STYLE


class Messager:
    def __init__(self, MessageLevel=LEVEL.INFO, MessageProgressLevel=LEVEL.INFO, NewProgress: Progress = None, NewProgressTrack: Callable[[Any], Iterable] = None) -> None:
        self._MessageLevel = MessageLevel
        self._MessageProgressLevel = MessageProgressLevel
        self.NewProgress = NewProgress
        self.NewTrackGenerator = NewProgressTrack

    @property
    def MessageLevel(self):
        return self._MessageLevel

    @MessageLevel.setter
    def MessageLevel(self, level):
        prev_level = self._MessageLevel
        self._MessageLevel = level
        return prev_level

    @property
    def MessageProgressLevel(self):
        return self._MessageProgressLevel

    @MessageProgressLevel.setter
    def MessageProgressLevel(self, level):
        prev_level = self._MessageProgressLevel
        self._MessageProgressLevel = level
        return prev_level

    # Recommeneded
    def message(self, *args, level=LEVEL.INFO, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if level >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_progress(self, sequence, *args, level=LEVEL.INFO, **kwargs):
        if level >= self._MessageProgressLevel:
            return self.NewTrackGenerator(sequence, *args, **kwargs)
        else:
            return sequence

    def new_progress(self, level=LEVEL.INFO):
        if level >= self._MessageProgressLevel:
            return self.NewProgress()
        else:
            return None

        # Others

    def debug(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.DEBUG >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def info(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.INFO >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def warning(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.WARNING >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def error(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.ERROR >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def critial(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.CRITICAL >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)