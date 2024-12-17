import io
import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import IO, NewType, TypeAlias, Union, cast

from libpycom.types import *


def handle_io(f: PathLike, content: bytes = None, mode: str = "r") -> bytes | None:
    if "r" in mode or "+" in mode:
        if hasattr(f, "read") and callable(f.read):
            return f.read()
        else:
            with open(f, mode) as readable:
                if content is None:
                    # 如果是纯读取或者读写模式且没有写入内容，则读取内容
                    return readable.read()
                else:
                    # 读写模式下，可以先读取再写入
                    data = readable.read()
                    readable.seek(0)  # 移动指针以便写入
                    readable.write(content)
                    readable.truncate()  # 截断文件以适应新写入内容
                    return data
    elif "w" in mode or "a" in mode:
        # 写入模式或附加模式
        if content is None:
            raise ValueError("Content must be provided when writing to a file.")

        if hasattr(f, "write") and callable(f.write):
            f.write(content)
        else:
            with open(f, mode) as writable:
                writable.write(content)
        return None
    else:
        raise ValueError(f"Unsupported mode: {mode}")


def load_bytes(f: PathLike) -> bytes:
    if hasattr(f, "read") and callable(cast(IO[bytes], f).read):
        content = cast(IO[bytes], f).read()
    else:
        f = cast(str | os.PathLike, f)
        with open(f, "rb") as readable:
            content = readable.read()
    return content


def save_bytes(content: bytes, f: PathLike) -> None:
    if hasattr(f, "write") and callable(cast(IO[bytes], f).write):
        cast(IO[bytes], f).write(content)
    else:
        f = cast(str | os.PathLike, f)
        with open(f, "wb") as writable:
            writable.write(content)


def load_texts(f: PathLike) -> bytes:
    if hasattr(f, "read") and callable(cast(IO[bytes], f).read):
        content = cast(IO[bytes], f).read()
    else:
        f = cast(str | os.PathLike, f)
        with open(f, "r") as readable:
            content = readable.read()
    return content


@contextmanager
def open_PathLike(f: PathLike, mode: str = "r"):
    if hasattr(f, "read") or hasattr(f, "write"):
        yield f
    else:
        f = cast(str | os.PathLike, f)
        with open(f, mode) as file:
            yield file


def save_texts(content: bytes, f: PathLike) -> None:
    if hasattr(f, "write") and callable(cast(IO[bytes], f).write):
        cast(IO[bytes], f).write(content)
    else:
        f = cast(str | os.PathLike, f)
        with open(f, "w") as writable:
            writable.write(content)


def count_lines(f: PathLike):
    if isinstance(f, io.IOBase):
        f = f.name
    
    # wc count \n in face, if the last line is not end with \n, it will not be counted
    result = subprocess.run(['wc', '-l', f], stdout=subprocess.PIPE)
    return int(result.stdout.split()[0])


def save_json(content, f: PathLike, **kwargs) -> None:
    import json

    from libpycom.SyntaxUtils import ClassUtils
    content = ClassUtils.encode(content)
    save_texts(json.dumps(content, **kwargs), f)

# def load_pickle(f: PathLike, content: bytes = None, mode: str = "r"):


if __name__ == "__main__":
    handle_io("./a.txt", "hello", "w")
