from typing import IO, TypeAlias
import numpy as np
import os
import pathlib

PathLike: TypeAlias = IO | str | os.PathLike | pathlib.Path

Array: TypeAlias = np.ndarray
