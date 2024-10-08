from sortedcontainers import SortedList

from libpycom.collections.Dict.DictWrapper import DictWrapper


class SortedValueDict(DictWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sorted_keys = SortedList(self._dict.keys(), key=self._dict.get)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        if key in self._dict:
            self._sorted_keys.remove(key)
        self._sorted_keys.add(key)

    def __delitem__(self, key):
        super().__delitem__(key)
        self._sorted_keys.remove(key)

    def __iter__(self):
        return iter(self._sorted_keys)

    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def clear(self):
        super().clear()
        self._sorted_keys.clear()

    def keys(self):
        return self._sorted_keys

    def values(self):
        return [self._dict[k] for k in self._sorted_keys]

    def items(self):
        return [(k, self._dict[k]) for k in self._sorted_keys]

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def pop(self, key, default=None):
        if key in self._dict:
            value = self._dict.pop(key)
            self._sorted_keys.remove(key)
            return value
        return default

    def popitem(self):
        key = self._sorted_keys.pop()
        value = self._dict.pop(key)
        return key, value

    def setdefault(self, key, default=None):
        if key not in self._dict:
            self[key] = default
        return self._dict[key]

    def refresh(self, key=None):
        """Refresh the sorted keys to ensure the order is correct."""
        if key is None:
            self._sorted_keys = SortedList(self._dict.keys(), key=self._dict.get)
        else:
            if key in self._sorted_keys:
                self._sorted_keys.remove(key)
            self._sorted_keys.add(key)
