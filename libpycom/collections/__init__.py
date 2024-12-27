__all__ = [
    'AccessibleDict',
    'SortedValueDict'
]

from types import EllipsisType
from libpycom.collections.Dict import *


class NullContainer:
    def __init__(self, *args, contains_value: bool | EllipsisType = False, **kwargs):
        self._data = dict(*args, **kwargs)
        self._contains_value = contains_value

    def __contains__(self, item):
        return item in self._data if self._contains_value is ... else self._contains_value
