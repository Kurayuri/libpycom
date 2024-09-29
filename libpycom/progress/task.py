from rich.progress import Progress, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn, MofNCompleteColumn
from typing import Any
from collections.abc import Iterable
import rich.progress


def new_progress(*args, **kwargs) -> Progress:
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


def new_progress_track(
    sequence: Iterable[Any],
    total: int | None = None,
    description: str = "",
) -> Iterable[Any]:

    progress = new_progress()

    if total is None:
        if hasattr(sequence, '__len__'):
            total = len(sequence)
        else:
            total = len([x for x in sequence])

    with progress:
        task = progress.add_task(description, total=total)
        for item in sequence:
            yield item
            progress.update(task, advance=1, total=total)
