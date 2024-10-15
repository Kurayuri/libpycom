import re
from collections.abc import MutableMapping
from datetime import datetime
from numbers import Number
import string
from types import EllipsisType
from typing import Any, Callable, Iterable
import unicodedata

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
    def format(_str, *args, **kwargs):

        return StrFormatter.format(_str, *args, **kwargs)

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

    @staticmethod
    def getWidth(_str):
        sum = 0
        for _char in _str:
            sum += CharUtils.getWidth(_char)
        return sum

    class FormatSpecUtils:
        '''
        https://docs.python.org/3/library/string.html#grammar-token-format-spec-format_spec

        format_spec     ::=  [[fill]align][sign]["z"]["#"]["0"][width][grouping_option]["." precision][type]
        fill            ::=  <any character>
        align           ::=  "<" | ">" | "=" | "^"
        sign            ::=  "+" | "-" | " "
        width           ::=  digit+
        grouping_option ::=  "_" | ","
        precision       ::=  digit+
        type            ::=  "b" | "c" | "d" | "e" | "E" | "f" | "F" | "g" | "G" | "n" | "o" | "s" | "x" | "X" | "%"
        '''
        FormatSpecRegex = r'''
        ^                            
        (?P<fill>.)?                 
        (?P<align>[<>=^])?           
        (?P<sign>[+\-\s])?           
        (?P<z>z)?                    
        (?P<hash>\#)?                
        (?P<zero>0)?                 
        (?P<width>[1-9]\d*)?         
        (?P<grouping_option>[_\,])?  
        (?P<precision>\.\d+)?        
        (?P<type>[bcdeEfFgGn%xoX])?  
        $                            
        '''
        FormatSpecKeys = ['fill', 'align', 'sign', 'z', 'hash', 'zero', 'width', 'grouping_option', 'precision', 'type']

        FormatSpecPattern = re.compile(FormatSpecRegex, re.VERBOSE)

        @classmethod
        def parse(cls, format_spec: str):
            match = cls.FormatSpecPattern.match(format_spec)
            if not match:
                raise ValueError(f"Invalid format_spec: {format_spec}")
            return match.groupdict()

        @classmethod
        def construct(cls, format_spec_dict):
            _new = ""
            for key in cls.FormatSpecKeys:
                v = format_spec_dict.get(key, "")
                _new += str(v) if v is not None else ""
            return _new


class CharUtils:
    @staticmethod
    def getWidth(_char):
        width_type = unicodedata.east_asian_width(_char)
        if width_type in ('F', 'W'):          # Fullwidth or Wide
            return 2
        elif width_type in ('H', 'Na', 'N'):  # Halfwidth, Narrow, Neutral
            return 1
        elif width_type == 'A':  # Ambiguous
            # 这里假设返回 1，但可以根据需要进行调整（例如在 East Asian 环境中可以设为 2）
            return 1
        else:
            return 1


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

    def get(_iterable: Iterable, index):
        if hasattr(_iterable, "__getitem__"):
            return _iterable[index]

        idx = 0
        for i in _iterable:
            if idx == index:
                return i
            idx += 1
        return None

    @staticmethod
    def align(_iterable, _value, _interval: Any | EllipsisType = ...):
        basevalue = IterableUtils.getFirst(_iterable)
        if _interval is ...:
            _interval = IterableUtils.get(_iterable, 1) - basevalue
        rounded_delta = ((_value - basevalue) // _interval) * _interval
        return basevalue + rounded_delta


class StrFormatter(string.Formatter):
    # https://docs.python.org/3/library/string.html#formatstrings

    def format_field(self, value, format_spec):
        format_spec_dict = StrUtils.FormatSpecUtils.parse(format_spec)
        ans = super().format_field(value, format_spec)
        cjk_num = StrUtils.getWidth(ans) - len(ans)
        if cjk_num != 0 and format_spec_dict['width'] is not None:
            format_spec_dict['width'] = str(int(format_spec_dict['width']) - cjk_num)
            format_spec = StrUtils.FormatSpecUtils.construct(format_spec_dict)
            ans = super().format_field(value, format_spec)

        return ans


StrFormatter = StrFormatter()
