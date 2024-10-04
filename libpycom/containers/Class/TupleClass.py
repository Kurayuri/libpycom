class TupleClass:
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs:
            setattr(self, k, v)

    def __iter__(self):
        return iter(self.__dict__.values())

    def __getitem__(self, index):
        return list(self.__dict__.values())[index]

    def __setitem__(self, index, value):
        keys = list(self.__dict__.keys())
        if index < len(keys):
            self.__dict__[keys[index]] = value
        else:
            raise IndexError("TupleClass index out of range")

    def __len__(self):
        return len(self.__dict__.values())

    @classmethod
    def from_obj(cls, obj):
        return cls(**obj.__dict__)
