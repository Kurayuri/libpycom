from libpycom.Messager import Messager


class __Settings__:
    def __init__(self) -> None:
        self._Messager = Messager()

    @property
    def MessageLevel(self):
        return self._Messager.MessageLevel

    @MessageLevel.setter
    def MessageLevel(self, level):
        return self._Messager.MessageLevel(level)

    @property
    def MessageProgressLevel(self):
        return self._Messager.MessageProgressLevel

    @MessageProgressLevel.setter
    def MessageProgressLevel(self, level):
        return self._Messager.MessageProgressLevel(level)
