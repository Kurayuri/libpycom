from libpycom.Const import LEVEL, STYLE
from libpycom import Settings


def message(*args, level=LEVEL.DEBUG, style=STYLE.RESET, end: str = "\n", separator: str = " "):
    if level >= 2:
        print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)


# def message_progress(sequence, description: str = "Processing", level=LEVEL.DEBUG):
#     if level >= Settings.MessageLevel:
#         return custom_track(sequence, description=description)
#     else:
#         return sequence
