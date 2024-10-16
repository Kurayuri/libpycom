from typing import IO, TypeAlias
import numpy as np
import os
import pathlib
from libpycom.metatypes import Sentinel, ValueEnum

Array: TypeAlias = np.ndarray

PathLike: TypeAlias = IO | str | os.PathLike | pathlib.Path

ListTuple: TypeAlias = list | tuple


Missing = Sentinel('Missing', bool_value=False)
NotGiven = Sentinel('NotGiven', bool_value=False)

ValueEnum = ValueEnum
