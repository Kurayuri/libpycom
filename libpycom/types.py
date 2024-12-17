import io
import sys
from typing import   TypeAlias
import numpy as np
import os
from libpycom.metatypes import Sentinel, ValueEnum, ClassWrapper, PostProcClass

__all__ = [
    "Array", "PathLike", "ListTuple", "Missing", "NotGiven", "ValueEnum", "ReprEnum", "ClassWrapper", "PostProcClass"
]

Array: TypeAlias = np.ndarray

PathLike: TypeAlias = io.IOBase | str | os.PathLike
PathStr = str | os.PathLike

ListTuple: TypeAlias = list | tuple


Missing = Sentinel('Missing', bool_value=False)
NotGiven = Sentinel('NotGiven', bool_value=False)

ValueEnum = ValueEnum
ClassWrapper = ClassWrapper
IterableClass = ClassWrapper
PostProcClass = PostProcClass

ReprEnum = ValueEnum
if sys.version_info >= (3, 11):
    from enum import ReprEnum
    ReprEnum = ReprEnum
