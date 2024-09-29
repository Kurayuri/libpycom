from libpycom.Const import LEVEL, STYLE
from libpycom import Settings


def message(*args, level=LEVEL.INFO, style=STYLE.RESET, end: str = "\n", separator: str = " "):
    if level >= Settings.MessageLevel:
        print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)


def message_progress(sequence, *args, level=LEVEL.INFO, **kwargs):
    if level >= Settings.MessageProgressLevel:
        Settings.messager.new_progress(*args, level, **kwargs)
        track = Settings.messager.fn_new_progress_track(sequence, *args, progress=Settings.messager._progress, **kwargs)
        return track
    else:
        return sequence


def message_enumprogress(sequence, *args, level=LEVEL.INFO, **kwargs):
    return enumerate(message_progress(sequence, *args, level=level, **kwargs))


def debug(*args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
    if LEVEL.DEBUG >= Settings.MessageLevel:
        print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)


def info(*args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
    if LEVEL.INFO >= Settings.MessageLevel:
        print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)


def warning(*args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
    if LEVEL.WARNING >= Settings.MessageLevel:
        print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)


def error(*args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
    if LEVEL.ERROR >= Settings.MessageLevel:
        print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)


def critial(*args, style=STYLE.RESET, end: str = "\n", separator: str = " "):
    if LEVEL.CRITICAL >= Settings.MessageLevel:
        print(f"{style}{separator.join(map(str, args))}{STYLE.RESET}", end=end)
