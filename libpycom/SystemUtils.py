import os
import pathlib
import shlex
import subprocess
import sys
import ctypes
from collections.abc import Iterable
from typing import Any


class ShellUtils:
    @staticmethod
    def join(args: str | Iterable[Any]):
        if isinstance(args, str):
            return args
        else:
            return shlex.join(map(str, args))

    @staticmethod
    def split(cmd: str):
        return shlex.split(cmd)

    @staticmethod
    def invoke(args: str | Iterable[Any]):
        args = ShellUtils.join(args)
        print(args)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)

        for line in iter(process.stdout.readline, ''):
            yield line.strip()

        process.stdout.close()
        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, args, output=None, stderr=process.stderr.read())

    @staticmethod
    def invokePython(args: str | Iterable[Any]):
        # args = ShellUtils.join(args)
        if isinstance(args, str):
            args = [args]
        python = sys.executable
        cmd = ShellUtils.join([python, *args])
        # print(cmd)
        return os.system(cmd)


class PathUtils:
    @staticmethod
    def resolve(path: str | os.PathLike):
        return (pathlib.Path(__file__).parent / path).resolve()


class InteractiveUtils:
    ITYPE_y_or_N = "y/N"
    ITYPE_Y_or_n = "Y/n"

    @staticmethod
    def confirmInput(prompt: str, default: bool = True) -> bool:
        print(prompt)
        choices = InteractiveUtils.ITYPE_Y_or_n if default else InteractiveUtils.ITYPE_y_or_N
        print(f"Proceed ({choices})? ", end="")
        response = input(prompt).lower()
        if response == "y" or response == "yes":
            return True
        else:
            return False


class CtypesUtils:
    @staticmethod
    def getLibRealpath(lib: ctypes.CDLL) -> str | None:
        """
        Get the actual file path of a shared library loaded via ctypes.CDLL.
        """
        search_name = os.path.basename(lib._name)
        
        with open("/proc/self/maps", "r") as f:
            for line in f:
                '''
                Perline:
                address perms offset dev inode pathname
                '''
                parts = line.split()
                if len(parts) >= 6:
                    path = parts[5]
                    if search_name in path and os.path.exists(path):
                        return path
        return None

if __name__ == "__main__":
    # test: CtypesUtils
    lib_name = "libstdc++.so"
    lib = ctypes.CDLL(lib_name)
    print(f"Library loaded from: {lib._name}")
    print(f"Library Actual path: {CtypesUtils.getLibRealpath(lib)}")