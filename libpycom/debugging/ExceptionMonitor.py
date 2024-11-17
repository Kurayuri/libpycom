class ExceptionMonitor:
    def __init__(self, *variables: tuple[str | None], suppressed: bool = False) -> None:
        self.variables = variables
        self.suppressed = suppressed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            print(("-" * 20 + "\n") * 3)
            print("Current global variables:")
            context = exc_traceback.tb_frame.f_locals
            if len(self.variables) != 0:
                if None in self.variables:
                    pass
                else:
                    for variable in self.variables:
                        print(f"{variable}: {context.get(variable)}")
            else:
                for k, valve in context.items():
                    print(f"{k}: {valve}")

        return self.suppressed
