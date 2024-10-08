from libpycom.Messager import Messager


class __Settings__:
    def __init__(self) -> None:
        self.messager = Messager()

    @property
    def MessageLevel(self) -> Messager.LEVEL:
        return self.messager.message_level

    @MessageLevel.setter
    def MessageLevel(self, level) -> None:
        self.messager.message_level = level

    @property
    def MessageProgressLevel(self) -> Messager.LEVEL:
        return self.messager.message_progress_level

    @MessageProgressLevel.setter
    def MessageProgressLevel(self, level) -> None:
        self.messager.message_progress_level = level
