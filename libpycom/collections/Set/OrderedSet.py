from collections.abc import MutableSet


class OrderedSet(MutableSet):
    def __init__(self, iterable=None) -> None:
        self._data = dict.fromkeys(iterable or [])

    def __contains__(self, value) -> bool:
        return value in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def add(self, value) -> None:
        self._data[value] = None

    def discard(self, value) -> None:
        self._data.pop(value, None)
