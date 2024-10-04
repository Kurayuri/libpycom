import re
from numbers import Number
from collections.abc import MutableMapping
from datetime import datetime
from typing import OrderedDict, Sequence


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
        def getDottedKey(_dict, dotted_key):
            keys = dotted_key.split('.')
            value = _dict

            for key in keys:
                value = value[key]
            return value

        @staticmethod
        def encode(_dict, *args, **kwargs):
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
        def itemsAll(_dict):
            def _itemsAll(_obj, parent_key=""):
                for k, v in _obj.items():
                    # full_key = f"{parent_key}.{k}" if parent_key else k
                    full_key = k

                    yield full_key, v

                    if isinstance(v, MutableMapping):
                        yield from _itemsAll(v, full_key)
            return _itemsAll(_dict)

    class Str:
        @staticmethod
        def formatFString(_str, _context):
            # Match {xxx.xxx}
            pattern = re.compile(r'\{([^\{\}]+)\}')

            def replace_match(match):
                dotted_key = match.group(1)
                return str(SyntaxUtils.Dict.getDottedKey(_context, dotted_key))

            return pattern.sub(replace_match, _str)

    class List:
        @staticmethod
        def encode(_list, *args, **kwargs):
            if isinstance(_list, list | tuple):
                ans = []
                for i in _list:
                    ans.append(SyntaxUtils.Class.encode(i))
                _list = type(_list)(ans)
            return _list
