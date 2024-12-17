
from itertools import islice
import os
from types import EllipsisType
from typing import Callable
from libpycom.io import count_lines


class CacheFile:
    FILENAME_PATTERN = "{path}.cache"

    def __init__(self, path: os.PathLike, filename_pattern: str | EllipsisType = ..., fn_cache: int | Callable | None = None):
        self.filename_pattern = self.FILENAME_PATTERN if filename_pattern is ... else filename_pattern
        self.fn_cache = fn_cache

        self.path = path
        self.cache_path = self.get_cache_path(path)

        self.cache_f = None
    
    def cache(self):
        print("Auto Cache")
        if isinstance(self.fn_cache, int):
            f = open(self.path, "rb")
            cache_f = open(self.cache_path, "wb")
            cache_f.writelines(islice(f, self.fn_cache))
            f.close()
            cache_f.close()
        if callable(self.fn_cache):
            self.fn_cache(self.path, self.cache_path)

    def open(self, mode: EllipsisType | str | bool = ...):
        if mode is ...:
            if self.check():
                mode = "rb"
            else:
                if self.fn_cache is not None:
                    # Auto Create cache
                    self.cache()
                    mode = "rb"
                else:
                    # Manual Create cache
                    mode = "wb"
        elif isinstance(mode, bool):
            mode = "rb" if mode else "wb"

        self.cache_f = open(self.cache_path, mode)
        return self.cache_f
    
    @property
    def cache_read(self):
        return "r" in self.cache_f.mode
    
    @property
    def cache_write(self):
        return not self.cache_read

    def get_cache_path(self, path):
        return self.filename_pattern.format(path=path)

    def check(self, strict=False):
        if os.path.exists(self.cache_path) and os.path.getmtime(self.cache_path) > os.path.getmtime(self.path):
            if strict:
                f_line = count_lines(self.path)
                cahce_line = count_lines(self.get_cache_path(self.path))
                print(f"File: {f_line}, Cache: {cahce_line}")
                return f_line == cahce_line
            else:
                return True
        else:
            return False