
from collections.abc import MutableSet


class SetWrapper(MutableSet):
    def __init__(self, iterable=None) -> None:
        self._data = set(iterable or [])

    def __contains__(self, x) -> bool:
        return x in self._data
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self) -> int:
        return len(self._data)
    
    def add(self, value) -> None:
        self._data.add(value)
    
    def discard(self, value) -> None:
        self._data.discard(value)