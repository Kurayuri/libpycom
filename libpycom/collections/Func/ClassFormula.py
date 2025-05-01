
from abc import abstractmethod
from copy import copy
import inspect
from typing import Iterable


class ClassFormula:
    def __init__(self) -> None:
        # Initialize the class at the end of child class __init__
        super().__init__()
        self.__bool_value__ = True
        self.__params__ = [param for param in self.__dict__ if not param.startswith("__") and not param.endswith("__")]
        self.__code__ = inspect.getsource(self._func).splitlines()[-1].strip().lstrip("return ").replace("self.", "")

    def __bool__(self):
        return self.__bool_value__

    @abstractmethod
    def _func(self, *args, **kwargs):
        ...

    @property
    def val(self):
        return self._func()

    @property
    def values(self):
        return {param: getattr(self, param) for param in self.__params__}

    @property
    def func(self):
        return self._func

    @property
    def code(self):
        return self.__code__

    def setNone(self):
        self.__bool_value__ = False

    def isNone(self):
        return not self.__bool_value__

    def __str__(self) -> str:
        return f"<ClassFormula {'' if self.__bool_value__ else False} Func: {self.code} Val: {self.val} Values: {self.values}>"

    __repr__ = __str__

    def clone(self):
        return copy(self)

    def __add__(self, other):
        _new = copy(self)
        _new.add_(other)
        return _new

    def add_(self, other):
        for param in self.__params__:
            setattr(self, param, getattr(self, param) + getattr(other, param))

    def __sub__(self, other):
        _new = copy(self)
        _new.sub_(other)
        return _new

    def sub_(self, other):
        for param in self.__params__:
            setattr(self, param, getattr(self, param) - getattr(other, param))

    @classmethod
    def sum(cls, formulas: Iterable):
        _new = None
        for formula in formulas:
            if _new is None:
                _new = formula.clone()
            else:
                _new.add_(formula)
        return _new
