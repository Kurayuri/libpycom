class FunctionHolder:
    def __init__(self, func, args=(), kwargs=None):
        self.func = func
        self.args = args
        self.kwargs = kwargs if kwargs is not None else {}

    def __call__(self, *args, **kwargs):
        return self.func(*(self.args+args), **{**self.kwargs, **kwargs})

