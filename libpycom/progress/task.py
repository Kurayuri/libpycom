from rich.progress import Progress, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn, MofNCompleteColumn
from typing import Any
from collections.abc import Iterable
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
                    total: int | None = None,
                    description: str = "",
                    progress: Progress | None = None,
                    ** kwargs) -> Iterable[Any]:

        if total is None:
            total = cls.measure_total(iterable)
        if total == 0 :
            total = None
        task = progress.add_task(description, total=total)
        for item in iterable:
            yield item
            progress.update(task, advance=1, total=total)
        # progress.stop_task(task)
