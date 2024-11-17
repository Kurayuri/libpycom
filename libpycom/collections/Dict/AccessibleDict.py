from collections.abc import MutableMapping
from libpycom.collections.Dict.DictWrapper import DictWrapper
from libpycom.SyntaxUtils import DictUtils


class AccessibleDict(DictWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set(self, keys, value):
        if not isinstance(keys, tuple):
            keys = (keys,)
        _dict = self._dict

        for key in keys[:-1]:
            _dict.setdefault(key, {})
            _dict = _dict[key]
        _dict[keys[-1]] = value

    def setdefault(self, keys, value=None, lazy=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        _dict = self._dict

        for key in keys[:-1]:
            _dict.setdefault(key, {})
            _dict = _dict[key]

        if lazy:
            if keys[-1] not in _dict:
                _dict[keys[-1]] = value()
            return _dict[keys[-1]]
        else:
            return _dict.setdefault(keys[-1], value)

    def get(self, keys, default=None, lazy=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        _dict = self._dict

        for key in keys:
            if isinstance(_dict, MutableMapping):
                _dict = _dict.get(key)
            else:
                _dict = None
            if _dict is None:
                _dict = default() if lazy else default
                break
        return _dict

    def update(self, other):
        def _update(d, u):
            for key, value in u.items():
                if isinstance(value, dict) and key in d and isinstance(d[key], dict):
                    _update(d[key], value)
                else:
                    d[key] = value

        _update(self._dict, other)

    def __setitem__(self, keys, value):
        if not isinstance(keys, tuple):
            keys = (keys,)
        self.set(keys, value)

    def encode(self, *args, **kwargs):
        return DictUtils.encode(self._dict, *args, **kwargs)
