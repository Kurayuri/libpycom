import os
import pathlib
import shlex
import subprocess
import sys
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
