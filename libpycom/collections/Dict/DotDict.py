class DotDict:
    """ Access dict with dot """

    def __init__(self, _dict: dict = None):
        if _dict is None:
            _dict = {}
        for key, value in _dict.items():
            if isinstance(value, dict):
                value = DotDict(value)
            setattr(self, key, value)

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self) -> str:
        return str(self.__dict__)
