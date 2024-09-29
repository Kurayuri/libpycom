from collections.abc import Iterable, Callable
from typing import Any
from rich.progress import Progress
from libpycom.Const import LEVEL, STYLE
from libpycom.progress.task import new_progress, new_progress_track


class Messager:
    def __init__(self, message_level: LEVEL = LEVEL.INFO, message_progress_level: LEVEL = LEVEL.INFO,
                 fn_new_progress: Callable[[Any], Progress] = new_progress,
                 fn_new_progress_track: Callable[[Any], Iterable[Any]] = new_progress_track) -> None:
        self._message_level = message_level
        self._message_progress_level = message_progress_level
        self.fn_new_progress = fn_new_progress
        self.fn_new_progress_track = fn_new_progress_track

    @property
    def message_level(self) -> LEVEL:
        return self._message_level

    @message_level.setter
    def message_level(self, level: LEVEL) -> None:
        self._message_level = level

    def set_message_level(self, level: LEVEL) -> LEVEL:
        prev_level = self._message_level
        self._message_level = level
        return prev_level

    @property
    def message_progress_level(self) -> LEVEL:
        return self._message_progress_level

    @message_progress_level.setter
    def message_progress_level(self, level: LEVEL) -> None:
        self._message_progress_level = level

    def set_message_progress_level(self, level: LEVEL) -> LEVEL:
        prev_level = self._message_progress_level
        self._message_progress_level = level
        return prev_level

    # Recommeneded
    def message(self, *args, level: LEVEL = LEVEL.INFO, style: STYLE = STYLE.RESET, end: str = "\n", separator: str = " ") -> None:
        if level >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_progress(self, sequence, *args, level=LEVEL.INFO, **kwargs) -> Iterable[Any]:
        if level >= self._message_progress_level:
            return self.fn_new_progress_track(sequence, *args, **kwargs)
        else:
            return sequence

    def message_enumprogress(self, sequence, *args, level=LEVEL.INFO, **kwargs):
        return enumerate(self.message_progress(sequence, *args, level=level, **kwargs))

    def new_progress(self, *args, level=LEVEL.INFO, **kwargs):
        if level >= self._message_progress_level:
            return self.fn_new_progress(*args, **kwargs)
        else:
            return None

        # Others

    def debug(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.DEBUG >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def info(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.INFO >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def warning(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.WARNING >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def error(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.ERROR >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def critial(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.CRITICAL >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)
