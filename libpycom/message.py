from libpycom import Settings
from typing import Callable, Iterable, Any
from rich.progress import Progress
from enum import IntEnum


class LEVEL(IntEnum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


MESSAGE_LEVEL = LEVEL


class STYLE:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


def message(*args, level=LEVEL.DEBUG, style=STYLE.RESET, end: str = "\n", separator: str = " "):
    if level >= Settings.MessageLevel:
        print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)


# def message_progress(sequence, description: str = "Processing", level=LEVEL.DEBUG):
#     if level >= Settings.MessageLevel:
#         return custom_track(sequence, description=description)
#     else:
#         return sequence


# class NoneProgress:
#     def __init__(self, *args, **kwargs):
#         pass

#     def add_task(self, description, total):
#         pass

#     def update(self, advance):
#         if self.current_task:
#             self.current_task['completed'] += advance
#             if self.current_task['completed'] >= self.current_task['total']:
#                 print(f"{self.current_task['description']} completed.")

#     def reset(self):
#         if self.current_task:
#             self.current_task['completed'] = 0


# # 使用示例
# if __name__ == "__main__":
#     progress = InvisibleProgress()
#     progress.add_task("Task 1", total=100)

#     for i in range(100):
#         progress.update(1)  # 更新进度


class Messager:
    def __init__(self, MessageLevel=LEVEL.INFO, MessageProgressLevel=LEVEL.INFO, NewProgress: Progress = None, NewProgressTrack: Callable[[Any], Iterable] = None) -> None:
        self._MessageLevel = MessageLevel
        self._MessageProgressLevel = MessageProgressLevel
        self.NewProgress = NewProgress
        self.NewTrackGenerator = NewProgressTrack

    @property
    def MessageLevel(self):
        return self._MessageLevel

    @MessageLevel.setter
    def MessageLevel(self, level):
        prev_level = self._MessageLevel
        self._MessageLevel = level
        return prev_level

    @property
    def MessageProgressLevel(self):
        return self._MessageProgressLevel

    @MessageProgressLevel.setter
    def MessageProgressLevel(self, level):
        prev_level = self._MessageProgressLevel
        self._MessageProgressLevel = level
        return prev_level

    # Recommeneded
    def message(self, *args, level=LEVEL.INFO, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if level >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def message_progress(self, sequence, *args, level=LEVEL.INFO, **kwargs):
        if level >= self._MessageProgressLevel:
            return self.NewTrackGenerator(sequence, *args, **kwargs)
        else:
            return sequence

    def new_progress(self, level=LEVEL.INFO):
        if level >= self._MessageProgressLevel:
            return self.NewProgress()
        else:
            return None

        # Others

    def debug(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.DEBUG >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def info(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.INFO >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def warning(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.WARNING >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def error(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.ERROR >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)

    def critial(self, *args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
        if LEVEL.CRITICAL >= self._MessageLevel:
            print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)
