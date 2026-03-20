from collections.abc import Iterable
from types import EllipsisType
from typing import Any, Callable

from rich.progress import (BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn,
                           TimeElapsedColumn, TimeRemainingColumn)

from libpycom.progress.abc import ProgressABC, ProgressUtils


class ProgressTask(ProgressABC):
    @classmethod
    def create(cls, *args, **kwargs) -> Progress:
        return Progress(
            SpinnerColumn(),
            MofNCompleteColumn(),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            "/",
            TimeRemainingColumn(),
            TextColumn("[progress.description]{task.description}")
        )

    @classmethod
    def attach_task(cls, iterable: Iterable[Any],
                    total: int | EllipsisType | None = ...,
                    description: str = "",
                    progress: Progress | None = None,
                    ** kwargs) -> Iterable[Any]:

        if total is ...:
            total = cls.measure_total(iterable)

        task = progress.add_task(description, total=total)
        for item in iterable:
            yield item
            progress.update(task, advance=1, total=total)
        # progress.stop_task(task)


class _Task:
    def __init__(self, parent=0, status=0, rich_task_id: int = 0):
        self.parent = parent
        self.status = status
        self.rich_task_id = rich_task_id


class ProgressManager:

    def __init__(self,
                 fn_new_progress: Callable[[Any], Progress] = ProgressTask.new,
                 fn_new_progress_track: Callable[[Any], Iterable[Any]] = ProgressTask.new_track):
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

    def _new_progress(self, *args, **kwargs):
        _progress = self.fn_new_progress(*args, **kwargs)
        if self._progress is not _progress:
            self._remove_progress()
            _progress.start()
        self._progress = _progress
        return self._progress

    def _remove_progress(self):
        ProgressUtils.remove(self._progress)
        self._progress = None

    def progress(self, iterable, *args, **kwargs):
        task_id = self._new_msg_task()

        if self._task_status[task_id].parent == 0:
            # Top Layer
            self._new_progress(*args, **kwargs)

        for item in self.fn_new_progress_track(iterable, *args, progress=self._progress, **kwargs):
            yield item

        self._task_status[task_id].status = 0

        if self._task_status[task_id].parent == 0:
            # Top Layer
            self._remove_progress()

    def enumprogress(self, iterable, *args, **kwargs):
        return enumerate(self.progress(iterable, *args, **kwargs))