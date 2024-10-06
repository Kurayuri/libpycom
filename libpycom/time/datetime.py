from datetime import datetime, timedelta
from types import EllipsisType
from typing import Iterable

__all__ = ['DatetimeUtils']


class DatetimeUtils:
    @staticmethod
    def convertFromTs(ts, basetime, _interval: timedelta | None = None, **kwargs):
        if _interval is None:
            _interval = timedelta(**kwargs)
        return basetime + _interval * ts

    @staticmethod
    def lookup(_time, _dict, _interval: timedelta | EllipsisType = ..., **kwargs):
        aligned_time = DatetimeUtils.align(_time, _dict, _interval, **kwargs)
        return _dict.get(aligned_time)

    @staticmethod
    def align(_time: datetime, _times: Iterable[datetime], _interval: timedelta | EllipsisType = ..., **kwargs):
        basetime = next(iter(_times))

        if kwargs:
            _interval = timedelta(**kwargs)

        elif _interval is ...:
            _interval = next(next(iter(_times))) - _time

        rounded_delta = ((_time - basetime) // _interval) * _interval
        return basetime + rounded_delta
