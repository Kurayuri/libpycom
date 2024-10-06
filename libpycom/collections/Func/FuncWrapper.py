class FuncWrapper:
    def __init__(self, _func, *args, **kwargs):
        self._func = _func
        self._args = args
        self._kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self._func(*(self._args + args), **{**self._kwargs, **kwargs})
