from collections.abc import Callable
from copy import copy
import inspect
from typing import Iterable


class Formula:
    def __init__(self, func: str | Callable | None):
        if func is None:
            self._func = None
            self._code = None
            return

        if isinstance(func, str):
            self._func = eval(func)
            self._code = func
        elif isinstance(func, Callable):
            self._func = func
            self._code = inspect.getsourcelines(func)[0]
        else:
            raise ValueError("func must be None or a string or a callable object.")

        self._params = inspect.signature(self._func).parameters
        for param in self._params:
            setattr(self, param, 0)

    @property
    def val(self):
        return self._func(*[getattr(self, param) for param in self._params]) if self._func is not None else None

    @property
    def values(self):
        return {param: getattr(self, param) for param in self._params} if self._func is not None else None

    @property
    def func(self):
        return self._func

    def setNone(self):
        self._func = None

    def isNone(self):
        return self._func is None

    def __str__(self) -> str:
        return f"<Formula> Func: {self._code} Val: {self.val} Values: {self.values}"

    # def copy(self):
    #     _new = Formula(self._func)
    #     for param in self._params:
    #         setattr(_new, param, getattr(self, param))
    #     return _new
    def clone(self):
        return copy(self)

    def __add__(self, other):
        # FIXME: 'self._func == other._func' is too strict
        if isinstance(other, Formula) and self._func == other._func and self._params == other._params:
            _new = copy(self)
            for param in self._params:
                setattr(_new, param, getattr(_new, param) + getattr(other, param))
            return _new
        else:
            raise ValueError("Both Formula objects must have the same function and parameter.")

    def add_(self, other):
        for param in self._params:
            setattr(self, param, getattr(self, param) + getattr(other, param))

    __repr__ = __str__

    @classmethod
    def sum(cls, formulas: Iterable):
        _new = None
        for formula in formulas:
            if _new is None:
                _new = formula.clone()
            else:
                _new.add_(formula)
        return _new
