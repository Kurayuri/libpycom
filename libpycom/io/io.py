from pathlib import Path
from libpycom.types import *
from typing import cast, NewType, Union, TypeAlias


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


def save_texts(content: bytes, f: PathLike) -> None:
    if hasattr(f, "write") and callable(cast(IO[bytes], f).write):
        cast(IO[bytes], f).write(content)
    else:
        f = cast(str | os.PathLike, f)
        with open(f, "w") as writable:
            writable.write(content)


import subprocess

def count_lines(f: PathLike):
    result = subprocess.run(['wc', '-l', f], stdout=subprocess.PIPE)
    return int(result.stdout.split()[0])


if __name__ == "__main__":
    handle_io("./a.txt", "hello", "w")
