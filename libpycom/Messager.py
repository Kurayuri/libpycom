from collections.abc import Callable, Iterable
from typing import Any

import libpycom
from libpycom.Const import LEVEL, STYLE
from libpycom.progress.task import ProgressTask
from rich.progress import Progress
from collections import namedtuple

Task = namedtuple('Task', ['parent', 'status'])


class Messager:
    def __init__(self, message_level: LEVEL = LEVEL.INFO, message_progress_level: LEVEL = LEVEL.INFO,
                 fn_new_progress: Callable[[Any], Progress] = ProgressTask.new,
                 fn_new_progress_track: Callable[[Any], Iterable[Any]] = ProgressTask.new_track) -> None:
        self._message_level = message_level
        self._message_progress_level = message_progress_level
        self.fn_new_progress = fn_new_progress
        self.fn_new_progress_track = fn_new_progress_track
        self._progress = None

        self._task_status = [Task(0, 0)]
        self._task_id = 0

    def _new_task(self):
        self._task_id += 1
        self._task_status.append(Task(0, 0))  # Parent, State: 0-Start,1-Stop
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

    def message(self, *args, level: LEVEL = LEVEL.INFO, style: STYLE = STYLE.RESET, end: str = "\n", separator: str = " ") -> None:
        if level >= self._message_level:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_progress(self, sequence, *args, level=LEVEL.INFO, **kwargs) -> Iterable[Any]:
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

            self._task_status[task_id] = Task(_prev, 1)

            for item in self.fn_new_progress_track(sequence, *args, progress=self._progress, ** kwargs):
                yield item

            self._task_status[task_id] = self._task_status[task_id]._replace(status=0)

            if self._task_status[task_id].parent == 0:
                # Top Layer
                self.remove_progress()
        else:
            return sequence

    def message_enumprogress(self, sequence, *args, level=LEVEL.INFO, **kwargs):
        return enumerate(self.message_progress(sequence, *args, level=level, **kwargs))

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
        libpycom.progress.abc.remove(self._progress)
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

#     def __del__(self):
#         try:
#             remove(self._progress)
#         except BaseException:
#             pass


# def cleanup():
#     remove(libpycom.messager._progress)


# atexit.register(cleanup)
