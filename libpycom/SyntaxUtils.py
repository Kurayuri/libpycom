import re
from collections.abc import MutableMapping
from datetime import datetime
from numbers import Number
from types import EllipsisType
from typing import Any, Callable, Iterable


class SyntaxUtils:
    class Class:
        @staticmethod
        def getAttrs(_obj):
            return {key: getattr(_obj, key) for key in dir(_obj)
                    if not key.startswith('__') and not key.endswith('__')}

        @staticmethod
        def encode(_obj, *args, **kwargs):
            if isinstance(_obj, str | Number | bool | None):
                return _obj
            elif isinstance(_obj, list | tuple):
                return SyntaxUtils.List.encode(_obj, *args, **kwargs)
            elif isinstance(_obj, MutableMapping):
                return SyntaxUtils.Dict.encode(_obj, *args, **kwargs)
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

    class Dict:
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
                        k = SyntaxUtils.Class.encode(k, *args, content=k_content, **kwargs)
                        ans[k] = v
                    return ans
                else:
                    _obj = SyntaxUtils.Class.encode(_obj, *args, content=o_content, **kwargs)

                return _obj

            return _encode(_dict)

        @staticmethod
        def map(_dict: MutableMapping, _funcs: Iterable[Callable], _types: Iterable[type], _filters: Iterable[Callable | EllipsisType | None] | None = None, strict: bool = False):
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
        def getFirst(_dict: MutableMapping) -> tuple[Any, Any]:
            for k, v in _dict.items():
                if isinstance(v, MutableMapping):
                    return SyntaxUtils.Dict.getFirst(v)
                else:
                    return k, v
            return None, None

    class Str:
        @staticmethod
        def formatFString(_str, _context):
            # Match {xxx.xxx}
            pattern = re.compile(r'\{([^\{\}]+)\}')

            def replace_match(match):
                dotted_key = match.group(1)
                return str(SyntaxUtils.Dict.getDottedKey(_context, dotted_key))

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

    class List:
        @staticmethod
        def encode(_list, *args, **kwargs):
            if isinstance(_list, list | tuple):
                ans = []
                for i in _list:
                    ans.append(SyntaxUtils.Class.encode(i))
                _list = type(_list)(ans)
            return _list

    class Iterable:
        @staticmethod
        def getFirst(_iterable):
            return next(iter(_iterable))


getFirst = SyntaxUtils.Iterable.getFirst
