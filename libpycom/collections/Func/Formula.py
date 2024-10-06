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

    __repr__ = __str__
