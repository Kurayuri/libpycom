from ast import Tuple
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


class _Task:
    def __init__(self, parent=0, status=0, rich_task_id: int = 0):
        self.parent = parent
        self.status = status
        self.rich_task_id = rich_task_id


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

        self._message_level, self._message_progress_level, self._log_level = \
            IterableUtils.fallback([message_level, message_progress_level, log_level], ..., level)

        super().__init__(name, self._log_level)
        self._logger = logging.Logger(name, level=self._log_level)
        self.fn_new_progress = fn_new_progress
        self.fn_new_progress_track = fn_new_progress_track
        self._progress = None

        self._task_status = [_Task(0, 0, 0)]
        self._task_id = 0  # Latest newed task's id

    def _new_msg_task(self):
        _id = self._task_id  # Latest newed task's id

        while _id:
            if self._task_status[_id].status == 1:  # id is running, thus id is new task's parent
                break
            _id = self._task_status[_id].parent

        self._task_id += 1
        self._task_status.append(_Task(_id, 1, 0))  # Parent, State: 0-Stop,1-Start

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

    @property
    def LogLevel(self) -> LEVEL:
        return self._logger.level

    @LogLevel.setter
    def LogLevel(self, level: LEVEL) -> None:
        self._logger.setLevel(level)

    def setLogLevel(self, level: LEVEL) -> LEVEL:
        prev_level = self.LogLevel
        self._logger.setLevel(level)
        return prev_level

    @property
    def Level(self) -> tuple[LEVEL, LEVEL, LEVEL]:
        return self._message_level, self._message_progress_level, self.LogLevel

    @Level.setter
    def Level(self, level: LEVEL) -> None:
        self.LogLevel = level
        self._message_level = level
        self._message_progress_level = level

    def setLevel(self, level: LEVEL) -> tuple[LEVEL, LEVEL, LEVEL]:
        prev_level = self.Level
        self.Level = level
        return prev_level

    # Recommeneded

    def message(self, *args, level: LEVEL = LEVEL.INFO, style: STYLE = STYLE.RESET,
                end: str = "\n", separator: str = " ") -> None:
        if level >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def start_progress_task(self, *args, level: LEVEL = LEVEL.INFO, **kwargs):
        if level >= self._message_progress_level:
            _task_id = self._new_msg_task()
            if self._task_status[_task_id].parent == 0:
                # Top Layer
                self._new_progress(*args, level, **kwargs)

            task_id = self._progress.add_task(*args, **kwargs)
            self._task_status[_task_id].rich_task_id = task_id

            return _task_id
        else:
            return None

    def stop_progress_task(self, task_id, level: LEVEL = LEVEL.INFO):
        if level >= self._message_progress_level:
            self._task_status[task_id].status = 1
            rich_task_id = self._task_status[task_id].rich_task_id
            self._progress.stop_task(rich_task_id)
            if self._task_status[task_id].parent == 0:
                # Top Layer
                self._remove_progress()

    def update_progress(self, task_id, *args, **kwargs):
        rich_task_id = self._task_status[task_id].rich_task_id
        self._progress.update(*args, task_id = rich_task_id,**kwargs)

    def advance_progress(self, task_id, *args, **kwargs):
        rich_task_id = self._task_status[task_id].rich_task_id

        self._progress.advance(*args, task_id = rich_task_id,**kwargs)

    def message_progress(self, iterable, *args, level: LEVEL = LEVEL.INFO, **kwargs) -> Iterable[Any]:
        if level >= self._message_progress_level:
            task_id = self._new_msg_task()

            if self._task_status[task_id].parent == 0:
                # Top Layer
                self._new_progress(*args, level, **kwargs)

            for item in self.fn_new_progress_track(iterable, *args, progress=self._progress, ** kwargs):
                yield item

            self._task_status[task_id].status = 0

            if self._task_status[task_id].parent == 0:
                # Top Layer
                self._remove_progress()
        else:
            yield from iterable

    def message_enumprogress(self, iterable, *args, level=LEVEL.INFO, **kwargs):
        return enumerate(self.message_progress(iterable, *args, level=level, **kwargs))

    def _new_progress(self, *args, level=LEVEL.INFO, **kwargs):
        _progress = self.fn_new_progress(*args, **kwargs)
        if self._progress is not _progress:
            self._remove_progress()
            _progress.start()
        self._progress = _progress
        if level >= self.MessageProgressLevel:
            return self._progress
        else:
            return None

    def _remove_progress(self):
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
