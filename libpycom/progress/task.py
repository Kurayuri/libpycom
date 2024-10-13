from collections.abc import Iterable
from types import EllipsisType
from typing import Any

from rich.progress import (BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TaskProgressColumn,
                           TimeElapsedColumn, TimeRemainingColumn)

from libpycom.progress.abc import ProgressABC


class ProgressTask(ProgressABC):
    @classmethod
    def create(cls, *args, **kwargs) -> Progress:
        return Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            MofNCompleteColumn(),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            "/",
            TimeRemainingColumn()
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
