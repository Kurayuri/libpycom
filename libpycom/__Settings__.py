from libpycom.Messager import Messager


class __Settings__:
    def __init__(self) -> None:
        self._messager = Messager()

    @property
    def MessageLevel(self):
        return self._messager.message_level

    @MessageLevel.setter
    def MessageLevel(self, level):
        return self._messager.message_level(level)

    @property
    def MessageProgressLevel(self):
        return self._messager.message_progress_level

    @MessageProgressLevel.setter
    def MessageProgressLevel(self, level):
        return self._messager.message_progress_level(level)
