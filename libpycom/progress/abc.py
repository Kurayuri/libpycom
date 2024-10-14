from abc import ABC, abstractmethod
from collections.abc import Iterable
from types import EllipsisType
from typing import Any

from rich.progress import Progress


class ProgressABC(ABC):
    TOTAL_AUTO = ...
    TOTAL_INF = -1

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> Progress:
        pass

    @classmethod
    @abstractmethod
    def attach_task(cls, iterable: Iterable[Any],
                    total: int | EllipsisType | None = ...,
                    description: str = "",
                    progress: Progress | None = None,
                    ** kwargs) -> Iterable[Any]:
        pass

    @classmethod
    def new(cls, *args, **kwargs) -> Progress:
        if ProgressUtils._progress is None:
            ProgressUtils._progress = cls.create(*args, **kwargs)
        return ProgressUtils._progress

    @classmethod
    def new_track(cls, iterable: Iterable[Any],
                  total: int | EllipsisType | None = ...,
                  description: str = "",
                  progress: Progress | None = None,
                  ** kwargs) -> Iterable[Any]:

        attached_progress = progress

        if progress is None:
            global_progress = ProgressUtils._progress

            _progress = cls.new()

            # Top Layer
            if _progress is not global_progress:
                _progress.start()
            # # # # # #
            progress = _progress

        for item in cls.attach_task(iterable, total, description, progress, ** kwargs):
            yield item

        if attached_progress is None:
            # Top Layer
            if _progress is not global_progress:
                cls.remove()
            # # # # # #

    @classmethod
    def remove(cls):
        ProgressUtils.remove()

    @classmethod
    def measure_total(cls, iterable: Iterable[Any]) -> int:
        if hasattr(iterable, '__len__'):
            total = len(iterable)
        else:
            total = 0
            for _ in iterable:
                total += 1
        return total


class ProgressUtils:
    _progress = None

    @classmethod
    def remove(cls, progress: Progress | EllipsisType = ...):
        if progress is ... or progress is cls._progress:
            progress = cls._progress
            cls._progress = None
        if hasattr(progress, 'stop'):
            progress.stop()
            return True
        return False
