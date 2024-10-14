import inspect


class Formula:
    def __init__(self, func):
        self._func = func
        self._params = inspect.signature(func).parameters
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
        return f"<Formula> Func: {inspect.getsourcelines(self._func)[0]} Val: {self.val} Values: {self.values}"

    def copy(self):
        _new = Formula(self._func)
        for param in self._params:
            setattr(_new, param, getattr(self, param))
        return _new

    def __add__(self, other):
        if isinstance(other, Formula) and self._func == other._func and self._params == other._params:

            _new = self.copy()
            for param in self._params:
                setattr(_new, param, getattr(_new, param) + getattr(other, param))
            return _new
        else:
            raise ValueError("Both Formula objects must have the same function and parameter.")

    __repr__ = __str__
