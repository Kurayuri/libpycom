from abc import ABC, abstractmethod
from collections.abc import Iterable
from types import EllipsisType
from typing import Any

from rich.progress import Progress


class ProgressABC(ABC):
    TOTAL_AUTO = ...
    TOTAL_INF = -1
    _progress = None

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
        if cls._progress is None:
            cls._progress = cls.create(*args, **kwargs)
        setattr(cls._progress, '_cls_ref', cls)
        return cls._progress

    @classmethod
    def new_track(cls, iterable: Iterable[Any],
                  total: int | EllipsisType | None = ...,
                  description: str = "",
                  progress: Progress | None = None,
                  ** kwargs) -> Iterable[Any]:

        attached_progress = progress

        if progress is None:
            cls_progress = cls._progress

            _progress = cls.new()

            # Top Layer
            if _progress is not cls_progress:
                _progress.start()
            # # # # # #
            progress = _progress

        for item in cls.attach_task(iterable, total, description, progress, ** kwargs):
            yield item

        if attached_progress is None:
            # Top Layer
            if _progress is not cls_progress:
                cls.remove()
            # # # # # #

    @classmethod
    def remove(cls):
        if cls._progress:
            cls._progress.stop()
        cls._progress = None

    @classmethod
    def measure_total(cls, iterable: Iterable[Any]) -> int:
        if hasattr(iterable, '__len__'):
            total = len(iterable)
        else:
            total = 0
            for _ in iterable:
                total += 1
        return total


def remove(progress: Progress) -> bool:
    if hasattr(progress, 'stop'):
        progress.stop()
        if hasattr(progress, '_cls_ref'):
            getattr(progress, '_cls_ref').remove()
            return True

    return False
