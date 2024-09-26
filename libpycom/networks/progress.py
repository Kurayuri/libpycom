import os
from rich.progress import Progress, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn, RenderableColumn, SpinnerColumn, TransferSpeedColumn, DownloadColumn
from typing import Iterable, Any


def new_progress():
    return Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        DownloadColumn(),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        "/",
        TimeRemainingColumn(),
        RenderableColumn(),
        TransferSpeedColumn(),
    )


def new_progress_track(
    sequence: Iterable[Any],
    total: int = None,
    description: str = "",
) -> Iterable[Any]:

    progress = new_progress()

    with progress:
        task = progress.add_task(description, total=total)
        for item in sequence:
            yield item
            progress.update(task, advance=len(item), total=total)


class FileProgressWrapper:
    def __init__(self, file, mode: str = 'rb', progress: Progress = None, chunk_size=1048576, **kwargs):
        self.file_path = file
        self.mode = mode  # Requried: requests/utils.py/super_len:'''if "b" not in o.mode'''
        self.file = open(file, mode, **kwargs)
        self.progress = progress
        self.chunk_size = chunk_size

        if progress:
            self.task = self.progress.add_task("", total=self.total)
            progress.start()

    @property
    def total(self):
        return os.path.getsize(self.file_path)

    def read(self, *args, **kwargs):
        chunk = self.file.read(self.chunk_size)
        if self.progress:
            self.progress.update(self.task, advance=len(chunk))
        return chunk

    def read_generator(self):
        while chunk := self.file.read(self.chunk_size):
            yield chunk
            if self.progress:
                self.progress.update(self.task, advance=len(chunk))

    # Requried:
    # requests/models.py/PreparedRequest/prepare_body/:'''is_stream=all([hasattr(data,"__iter__"),notisinstance(data,(basestring,list,tuple,Mapping)),])''',
    # used for exam body whether is stream

    def __iter__(self):
        return self.file.__iter__()

    def __next__(self):
        return self.file.__next__()

    # Requried:
    # requests/utils.py/super_len:'''fileno = o.fileno()''', used for getting file size
    def fileno(self):
        return self.file.fileno()

    def __del__(self):
        self.close()

    def close(self):
        self.file.close()
        if self.progress:
            self.progress.stop()
