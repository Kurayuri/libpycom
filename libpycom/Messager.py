from collections import namedtuple
from collections.abc import Callable, Iterable
from types import EllipsisType
from typing import Any

from rich.progress import Progress

from libpycom.progress import ProgressUtils, ProgressTask

__all__ = ['Messager', 'LEVEL', 'STYLE']


_Task = namedtuple('Task', ['parent', 'status'])


class Messager:
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

    class LEVEL:
        DEBUG = 1
        INFO = 2
        WARNING = 3
        ERROR = 4
        CRITICAL = 5

    class STYLE:
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"
        RESET = "\033[0m"

    def __init__(self, message_level: LEVEL = LEVEL.INFO, message_progress_level: LEVEL = LEVEL.INFO,
                 fn_new_progress: Callable[[Any], Progress] = ProgressTask.new,
                 fn_new_progress_track: Callable[[Any], Iterable[Any]] = ProgressTask.new_track) -> None:
        self._message_level = message_level
        self._message_progress_level = message_progress_level
        self.fn_new_progress = fn_new_progress
        self.fn_new_progress_track = fn_new_progress_track
        self._progress = None

        self._task_status = [_Task(0, 0)]
        self._task_id = 0

    def _new_task(self):
        self._task_id += 1
        self._task_status.append(_Task(0, 0))  # Parent, State: 0-Start,1-Stop
        return self._task_id

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

    def message(self, *args, level: LEVEL = LEVEL.INFO, style: STYLE = STYLE.RESET,
                end: str = "\n", separator: str = " ") -> None:
        if level >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_progress(self, iterable, *args,
                         total: int | EllipsisType | None = ..., description: str = "", level=LEVEL.INFO,
                         **kwargs) -> Iterable[Any]:
        if level >= self._message_progress_level:
            prev_task_id = self._task_id
            _prev = prev_task_id
            task_id = self._new_task()

            while _prev:
                if self._task_status[_prev].status == 1:
                    break
                _prev = self._task_status[_prev].parent
            else:
                # Top Layer
                self.new_progress(*args, level, **kwargs)

            self._task_status[task_id] = _Task(_prev, 1)

            yield from self.fn_new_progress_track(iterable, *args, total=total,
                                                  description=description, progress=self._progress, ** kwargs)

            self._task_status[task_id] = self._task_status[task_id]._replace(status=0)

            if self._task_status[task_id].parent == 0:
                # Top Layer
                self.remove_progress()
        else:
            yield from iterable

    def message_enumprogress(self, iterable, *args,
                             total: int | EllipsisType | None = ..., description: str = "", level=LEVEL.INFO,
                             **kwargs):
        return enumerate(self.message_progress(iterable, *args,
                                               total=total, description=description, level=level,
                                               **kwargs))

    def new_progress(self, *args, level=LEVEL.INFO, **kwargs):
        _progress = self.fn_new_progress(*args, **kwargs)
        if self._progress is not _progress:
            self.remove_progress()
            _progress.start()
        self._progress = _progress
        if level >= self._message_progress_level:
            return self._progress
        else:
            return None

    def remove_progress(self):
        ProgressUtils.remove(self._progress)
        self._progress = None

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


LEVEL = Messager.LEVEL
STYLE = Messager.STYLE

# Abnormal exit
#     def __del__(self):
#         try:
#             remove(self._progress)
#         except BaseException:
#             pass


# def cleanup():
#     remove(libpycom.messager._progress)


# atexit.register(cleanup)
