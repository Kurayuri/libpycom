"""
Unique sentinel values.
PEP 661 https://peps.python.org/pep-0661/

"""

import sys

_registry = {}


class Sentinel:
    def __new__(cls, name, repr=None, bool_value=True, module_name=None):
        name = str(name)
        repr = str(repr) if repr else f'<{name.split(".")[-1]}>'
        bool_value = bool(bool_value)
        if module_name is None:
            try:
                module_name = \
                    sys._getframe(1).f_globals.get('__name__', '__main__')
            except (AttributeError, ValueError):
                module_name = __name__

        registry_key = f'{module_name}-{name}'

        sentinel = _registry.get(registry_key, None)
        if sentinel is not None:
            return sentinel

        sentinel = super().__new__(cls)
        sentinel._name = name
        sentinel._repr = repr
        sentinel._bool_value = bool_value
        sentinel._module_name = module_name

        return _registry.setdefault(registry_key, sentinel)

    def __repr__(self):
        return self._repr

    def __bool__(self):
        return self._bool_value

    def __reduce__(self):
        return (
            self.__class__,
            (
                self._name,
                self._repr,
                self._module_name,
            ),
        )


class ValueEnumMeta(type):
    def __iter__(cls):
        return iter(cls._mamber_map_.values())

    def __len__(cls):
        return len(cls._mamber_map_)

    def __contains__(cls, item):
        return item in cls._mamber_map_.values()

    def __getattr__(cls, item):
        if item in cls._mamber_map_:
            return cls._mamber_map_[item]
        raise AttributeError(f"{cls.__name__} has no attribute '{item}'")


class ValueEnum(metaclass=ValueEnumMeta):
    _mamber_map_ = {}

    def __init_subclass__(cls):
        for key, value in cls.__dict__.items():
            if not key.startswith('_'):
                cls._mamber_map_[key] = value
