from collections import namedtuple
from collections.abc import Callable, Iterable
import logging
from types import EllipsisType
from typing import Any

from libpycom.SyntaxUtils import IterableUtils
from libpycom.types import ReprEnum
from rich.progress import Progress
from libpycom.progress import ProgressUtils, ProgressTask

__all__ = ['Messager', 'LEVEL', 'STYLE']


_Task = namedtuple('Task', ['parent', 'status'])
_regestry = {}


class Messager(logging.Logger):

    class LEVEL(int, ReprEnum):
        NOTSET = logging.NOTSET
        DEBUG = logging.DEBUG
        INFO = logging.INFO
        WARNING = logging.WARNING
        ERROR = logging.ERROR
        CRITICAL = logging.CRITICAL

    class STYLE(str, ReprEnum):
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

    def __init__(self, name: str = "", level: LEVEL = LEVEL.NOTSET,
                 message_level: LEVEL | EllipsisType = ...,
                 message_progress_level: LEVEL | EllipsisType = ...,
                 log_level: LEVEL | EllipsisType = ...,
                 fn_new_progress: Callable[[Any], Progress] = ProgressTask.new,
                 fn_new_progress_track: Callable[[Any], Iterable[Any]] = ProgressTask.new_track) -> None:
        super().__init__(name, level)

        self._logger = logging.Logger(name, level=level)

        self._message_level, self._message_progress_level, self._log_level = \
            IterableUtils.fallback([message_level, message_progress_level, log_level], ..., level)

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
    def MessageLevel(self) -> LEVEL:
        return self._message_level

    @MessageLevel.setter
    def MessageLevel(self, level: LEVEL) -> None:
        self._message_level = level

    def setMessageLevel(self, level: LEVEL) -> LEVEL:
        prev_level = self._message_level
        self._message_level = level
        return prev_level

    @property
    def MessageProgressLevel(self) -> LEVEL:
        return self._message_progress_level

    @MessageProgressLevel.setter
    def MessageProgressLevel(self, level: LEVEL) -> None:
        self._message_progress_level = level

    def setMessageProgressLevel(self, level: LEVEL) -> LEVEL:
        prev_level = self._message_progress_level
        self._message_progress_level = level
        return prev_level

    # Recommeneded

    def message(self, *args, level: LEVEL = LEVEL.INFO, style: STYLE = STYLE.RESET,
                end: str = "\n", separator: str = " ") -> None:
        if level >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_progress(self, iterable, *args, level: LEVEL = LEVEL.INFO, **kwargs) -> Iterable[Any]:
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

            for item in self.fn_new_progress_track(iterable, *args, progress=self._progress, ** kwargs):
                yield item

            self._task_status[task_id] = self._task_status[task_id]._replace(status=0)

            if self._task_status[task_id].parent == 0:
                # Top Layer
                self.remove_progress()
        else:
            return iterable

    def message_enumprogress(self, iterable, *args, level=LEVEL.INFO, **kwargs):
        return enumerate(self.message_progress(iterable, *args, level=level, **kwargs))

    def new_progress(self, *args, level=LEVEL.INFO, **kwargs):
        _progress = self.fn_new_progress(*args, **kwargs)
        if self._progress is not _progress:
            self.remove_progress()
            _progress.start()
        self._progress = _progress
        if level >= self.MessageProgressLevel:
            return self._progress
        else:
            return None

    def remove_progress(self):
        ProgressUtils.remove(self._progress)
        self._progress = None

    # Others
    def message_debug(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.DEBUG >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_info(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.INFO >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_warning(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.WARNING >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_error(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.ERROR >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_critical(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.CRITICAL >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    debug = message_debug
    info = message_info
    warning = message_warning
    error = message_error
    critical = message_critical

    def log_debug(self, *args, **kwargs):
        super().debug(*args, **kwargs)

    def log_info(self, *args, **kwargs):
        super().info(*args, **kwargs)

    def log_warning(self, *args, **kwargs):
        super().warning(*args, **kwargs)

    def log_error(self, *args, **kwargs):
        super().error(*args, **kwargs)

    def log_critical(self, *args, **kwargs):
        super().critical(*args, **kwargs)

    NOTSET = LEVEL.NOTSET
    DEBUG = LEVEL.DEBUG
    INFO = LEVEL.INFO
    WARNING = LEVEL.WARNING
    ERROR = LEVEL.ERROR
    CRITICAL = LEVEL.CRITICAL

    RED = STYLE.RED
    GREEN = STYLE.GREEN
    YELLOW = STYLE.YELLOW
    BLUE = STYLE.BLUE
    MAGENTA = STYLE.MAGENTA
    CYAN = STYLE.CYAN
    WHITE = STYLE.WHITE
    BOLD = STYLE.BOLD
    UNDERLINE = STYLE.UNDERLINE
    RESET = STYLE.RESET

# Abnormal exit
#     def __del__(self):
#         try:
#             remove(self._progress)
#         except BaseException:
#             pass


# def cleanup():
#     remove(libpycom.messager._progress)


# atexit.register(cleanup)


LEVEL = Messager.LEVEL
STYLE = Messager.STYLE

NOTSET = LEVEL.NOTSET
DEBUG = LEVEL.DEBUG
INFO = LEVEL.INFO
WARNING = LEVEL.WARNING
ERROR = LEVEL.ERROR
CRITICAL = LEVEL.CRITICAL

RED = STYLE.RED
GREEN = STYLE.GREEN
YELLOW = STYLE.YELLOW
BLUE = STYLE.BLUE
MAGENTA = STYLE.MAGENTA
CYAN = STYLE.CYAN
WHITE = STYLE.WHITE
BOLD = STYLE.BOLD
UNDERLINE = STYLE.UNDERLINE
RESET = STYLE.RESET


def getMessager(name):
    return _regestry.get(name, Messager(name))
