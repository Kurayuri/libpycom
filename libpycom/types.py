import sys
from typing import IO, TypeAlias
import numpy as np
import os
import pathlib
from libpycom.metatypes import Sentinel, ValueEnum

__all__ = [
    "Array", "PathLike", "ListTuple", "Missing", "NotGiven", "ValueEnum", "ReprEnum"
]

Array: TypeAlias = np.ndarray

PathLike: TypeAlias = IO | str | os.PathLike | pathlib.Path
PathStr = str | os.PathLike

ListTuple: TypeAlias = list | tuple


Missing = Sentinel('Missing', bool_value=False)
NotGiven = Sentinel('NotGiven', bool_value=False)

ValueEnum = ValueEnum

ReprEnum = ValueEnum
if sys.version_info >= (3, 11):
    from enum import ReprEnum
    ReprEnum = ReprEnum
