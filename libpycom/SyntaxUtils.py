import re
from collections.abc import MutableMapping
from datetime import datetime
from numbers import Number
from types import EllipsisType
from typing import Any, Callable, Iterable

from libpycom.aliases import ListTuple

__all__ = [
    'ClassUtils', 'DictUtils', 'StrUtils', 'ListTupleUtils', 'IterableUtils'
]


class ClassUtils:
    @staticmethod
    def getAttrs(_obj):
        return {key: getattr(_obj, key) for key in dir(_obj)
                if not key.startswith('__') and not key.endswith('__')}

    @staticmethod
    def encode(_obj, *args, **kwargs):
        if isinstance(_obj, str | Number | bool | None):
            return _obj
        elif isinstance(_obj, ListTuple):
            return ListTupleUtils.encode(_obj, *args, **kwargs)
        elif isinstance(_obj, MutableMapping):
            return DictUtils.encode(_obj, *args, **kwargs)
        elif isinstance(_obj, datetime):
            return _obj.isoformat()
        elif hasattr(_obj, "encode"):
            return _obj.encode(*args, **kwargs)
        elif hasattr(_obj, "__str__"):
            return str(_obj)
        elif hasattr(_obj, '__repr__'):
            return repr(_obj)
        else:
            return _obj


class DictUtils:
    @staticmethod
    def getDottedKey(_dict: MutableMapping, dotted_key):
        keys = dotted_key.split('.')
        value = _dict

        for key in keys:
            value = value[key]
        return value

    @staticmethod
    def encode(_dict: MutableMapping, *args, **kwargs):
        k_content = kwargs.get('content', False)
        o_content = kwargs.pop('content', True)

        def _encode(_obj):
            if isinstance(_obj, MutableMapping):
                ans = {}
                for k, v in _obj.items():
                    v = _encode(v)
                    k = ClassUtils.encode(k, *args, content=k_content, **kwargs)
                    ans[k] = v
                return ans
            else:
                _obj = ClassUtils.encode(_obj, *args, content=o_content, **kwargs)

            return _obj

        return _encode(_dict)

    @staticmethod
    def map(_dict: MutableMapping, _funcs: Iterable[Callable], _types: Iterable[type],
            _filters: Iterable[Callable | EllipsisType | None] | None = None, strict: bool = False):
        '''
        _filter = {
            Callable: call to check, true so map
            EllipsisType:  try to map all matched type, if exception, ignore
            None: map all matched type
        }
        '''
        _func_dict = {}
        _filter_dict = {}

        if strict:
            for _func, _type in zip(_funcs, _types):
                _func_dict[_type] = _func

        if _filters:
            for _type, _filter in zip(_types, _filters):
                _filter_dict[_type] = _filter

        def _call(_obj, _func):
            _filter = _filter_dict.get(type(_obj))
            if _filter is ...:
                try:
                    return _func(_obj) if _func else _obj
                except BaseException:
                    return _obj
            else:
                if _filter and not _filter(_obj):
                    _func = None

                return _func(_obj) if _func else _obj

        def _map_obj(_obj):
            if strict:
                _func = _func_dict.get(type(_obj))
                return _call(_obj, _func)
            else:
                for _func, _type in zip(_funcs, _types):
                    if isinstance(_obj, _type):
                        return _call(_obj, _func)
                return _obj

        def _map(_obj):
            ans = {}
            for k, v in _obj.items():
                k = _map_obj(k)
                if isinstance(v, MutableMapping):
                    v = _map(v)
                else:
                    v = _map_obj(v)
                ans[k] = v
            return ans

        return _map(_dict)

    @staticmethod
    def reshape(_dict: MutableMapping, shape: tuple[int]):
        _shape_map = []

        for id, level in enumerate(shape):
            _shape_map += [id] * level

        def shouldCompress(level):
            if level < len(_shape_map):
                return _shape_map[level - 1] == _shape_map[level]
            return False

        ans = {}

        def _reshape(d, curr_level):
            if curr_level > len(_shape_map):  # No more levels to compress
                return d

            _ans = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    v = _reshape(v, curr_level + 1)

                    if shouldCompress(curr_level):  # If current level should be compressed
                        for _k, _v in v.items():
                            if not isinstance(_k, tuple):
                                _k = (_k,)

                            new_k = (k,) + _k
                            _ans[new_k] = _v
                        continue
                _ans[k] = v
            return _ans

        ans = _reshape(_dict, 1)
        return ans

    @staticmethod
    def compare(dict1, dict2, path=""):
        differences = []

        # 检查 dict1 中的键
        for key in dict1:
            if key not in dict2:
                differences.append(f"{path}/{key} : Only in dict1")
            else:
                # 如果值也是字典，则递归比较
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    differences.extend(DictUtils.compare(dict1[key], dict2[key], path + "/" + str(key)))
                # 否则比较值
                elif dict1[key] != dict2[key]:
                    differences.append(f"{path}/{key} : dict1 = {dict1[key]}, dict2 = {dict2[key]}")

        # 检查 dict2 中的键
        for key in dict2:
            if key not in dict1:
                differences.append(f"{path}/{key} : Only in dict2")

        return differences

    @staticmethod
    def itemsAll(_dict: MutableMapping):
        def _itemsAll(_obj, parent_key=""):
            for k, v in _obj.items():
                # full_key = f"{parent_key}.{k}" if parent_key else k
                full_key = k

                yield full_key, v

                if isinstance(v, MutableMapping):
                    yield from _itemsAll(v, full_key)
        return _itemsAll(_dict)

    @staticmethod
    def getFirstItem(_dict: MutableMapping) -> tuple[Any, Any]:
        for k, v in _dict.items():
            if isinstance(v, MutableMapping):
                return DictUtils.getFirstItem(v)
            else:
                return k, v
        return None, None

    @staticmethod
    def getFirstValue(_dict: MutableMapping) -> Any:
        for k, v in _dict.items():
            if isinstance(v, MutableMapping):
                return DictUtils.getFirstValue(v)
            else:
                return v
        return None

    @staticmethod
    def getFirstKey(_dict: MutableMapping) -> Any:
        for k, v in _dict.items():
            if isinstance(v, MutableMapping):
                return DictUtils.getFirstKey(v)
            else:
                return k
        return None

    getFirst = getFirstKey


class StrUtils:
    @staticmethod
    def formatFString(_str, _context):
        # Match {xxx.xxx}
        pattern = re.compile(r'\{([^\{\}]+)\}')

        def replace_match(match):
            dotted_key = match.group(1)
            return str(DictUtils.getDottedKey(_context, dotted_key))

        return pattern.sub(replace_match, _str)

    @staticmethod
    def isNumber(_str) -> bool:
        try:
            float(_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def toNumber(_str):
        n = float(_str)
        return int(n) if n.is_integer() else n


class ListTupleUtils:
    @staticmethod
    def encode(_list, *args, **kwargs):
        if isinstance(_list, ListTuple):
            ans = []
            for i in _list:
                ans.append(ClassUtils.encode(i))
            _list = type(_list)(ans)
        return _list


class IterableUtils:
    @staticmethod
    def getFirst(_iterable):
        return next(iter(_iterable))
