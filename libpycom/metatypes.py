"""
Unique sentinel values.
PEP 661 https://peps.python.org/pep-0661/

"""

from collections.abc import MutableMapping
import sys
from types import EllipsisType, MappingProxyType


_registry = {}


class ClassWrapperMeta(type):
    def __new__(mcls, name, bases, class_dict, key_based=False):
        cls = super().__new__(mcls, name, bases, class_dict)

        cls.__member_map__ = {}
        cls.__match_key__ = key_based
        '''
        # Deprecated: use Method Resolution Order (MRO) instead
        def register_attr(obj):
            # class and its bases
            if isinstance(obj, type):
                register_attr(obj.__bases__)
                register_attr(obj.__dict__)
            # bases
            elif isinstance(obj, list | tuple):
                for item in obj:
                    register_attr(item)
            # class_dict
            elif isinstance(obj, MappingProxyType | MutableMapping):
                for key, value in obj.items():
                    if not key.startswith('__'):
                        cls.__member_map__[key] = value

        # inherited class
        register_attr(bases)
        # current class
        register_attr(class_dict)
        '''
        def register_attr(obj):
            # class's bases and itself
            if isinstance(obj, type):
                # register_attr(obj.__mro__[:0:-1])

                register_attr(obj.__dict__)
                # use __member_map__ to override the inherited class
                if hasattr(obj, '__member_map__'):
                    cls.__member_map__.update(obj.__member_map__)

            # bases
            elif isinstance(obj, list | tuple):
                for item in obj:
                    register_attr(item)

            # class_dict
            elif isinstance(obj, MappingProxyType | MutableMapping):
                for key, value in obj.items():
                    if not key.startswith('__'):
                        cls.__member_map__[key] = value

        '''MRO register'''
        register_attr(cls.__mro__[:0:-1])
        register_attr(class_dict)

        return cls

    def __iter__(cls):
        if cls.__match_key__:
            return iter(cls.__member_map__.keys())
        else:
            return iter(cls.__member_map__.values())

    def __len__(cls):
        return len(cls.__member_map__)

    def __contains__(cls, item):
        if cls.__match_key__:
            return item in cls.__member_map__.keys()
        else:
            return item in cls.__member_map__.values()

    def __getattr__(cls, item):
        return cls.__member_map__[item]

    def __getattribute__(cls, name):
        if not name.startswith('__') and name in cls.__member_map__:
            return cls.__member_map__[name]
        else:
            return super().__getattribute__(name)

    def __setattr__(cls, name, value):
        if not name.startswith('__'):
            cls.__member_map__[name] = value
        super().__setattr__(name, value)

    def __delattr__(cls, name: str, /) -> None:
        if not name.startswith('__') and name in cls.__member_map__:
            del cls.__member_map__[name]
        return super().__delattr__(name)

    def __items__(cls):
        return cls.__member_map__.items()

    def __keys__(cls):
        return cls.__member_map__.keys()

    def __values__(cls):
        return cls.__member_map__.values()


class ClassWrapper(metaclass=ClassWrapperMeta):
    ...


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
        return iter(cls.__member_map__.values())

    def __len__(cls):
        return len(cls.__member_map__)

    def __contains__(cls, item):
        return item in cls.__member_map__.values()

    def __getattr__(cls, item):
        if item in cls.__member_map__:
            return cls.__member_map__[item]
        raise AttributeError(f"{cls.__name__} has no attribute '{item}'")

    def __repr__(cls) -> str:
        return f"<enum '{cls.__name__}'>"

    def add(cls, name, value):
        setattr(cls, name, value)
        cls.__member_map__[name] = value

    def update(cls, other):
        for name, value in other.__member_map__.items():
            cls.add(name, value)

    def union(cls, other, typename: str | EllipsisType = ...):
        if typename is ...:
            typename = f"{cls.__name__} | {other.__name__}"
        result = cls.copy(typename)
        result.update(other)
        return result

    def copy(cls, typename: str | EllipsisType = ...):
        if typename is ...:
            typename = f"{cls.__name__}"
        result = type(typename, (cls,), {})
        result.update(cls)
        return result


class ValueEnum(metaclass=ValueEnumMeta):
    def __init_subclass__(cls):
        cls.__member_map__ = {}
        for key, value in cls.__dict__.items():
            if not key.startswith('__'):
                cls.__member_map__[key] = value


class PostProcClassMeta(ClassWrapperMeta):
    def __new__(cls, *args, post_proc=lambda x: x, proc_name=False, **kwargs):
        cls = super().__new__(cls, *args, **kwargs)
        cls.__post_proc__ = post_proc
        cls.__proc_name__ = proc_name

        attr_names = list(cls.__member_map__.keys())
        for attr_name in attr_names:
            setattr(cls, attr_name, cls.__member_map__[attr_name])
        return cls

    def __proc__(cls, name, value):
        if cls.__proc_name__:
            return cls.__post_proc__(name, value)
        else:
            return name, cls.__post_proc__(value)

    def __setattr__(cls, name, value):
        _name = name
        if not name.startswith('__'):
            name, value = cls.__proc__(name, value)
        super().__setattr__(name, value)
        if _name != name and _name in cls.__dict__:
            delattr(cls, _name)


class PostProcClass(metaclass=PostProcClassMeta):
    ...
