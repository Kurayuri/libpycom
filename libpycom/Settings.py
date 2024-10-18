from libpycom.Messager import Messager


class SettingsClass:
    def __init__(self) -> None:
        self.messager = Messager()

    @property
    def MessageLevel(self) -> Messager.LEVEL:
        return self.messager.MessageLevel

    @MessageLevel.setter
    def MessageLevel(self, level) -> None:
        self.messager.MessageLevel = level

    @property
    def MessageProgressLevel(self) -> Messager.LEVEL:
        return self.messager.MessageProgressLevel

    @MessageProgressLevel.setter
    def MessageProgressLevel(self, level) -> None:
        self.messager.MessageProgressLevel = level


Settings = SettingsClass()
messager = Settings.messager
