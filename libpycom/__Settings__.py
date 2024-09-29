from libpycom.Messager import Messager


class __Settings__:
    def __init__(self) -> None:
        self.messager = Messager()

    @property
    def MessageLevel(self):
        return self.messager.message_level

    @MessageLevel.setter
    def MessageLevel(self, level):
        self.messager.message_level = level

    @property
    def MessageProgressLevel(self):
        return self.messager.message_progress_level

    @MessageProgressLevel.setter
    def MessageProgressLevel(self, level):
        self.messager.message_progress_level = level

