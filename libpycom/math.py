from typing import Iterable
import numpy as np


def safe_div(a, b, default=0.0):
    try:
        ans = a / b
        return default if np.isnan(ans) or ans is None else ans
    except BaseException:
        return default


def ewma(iterable: Iterable[float], alpha: float, init_val: float | None = None,
         start: int | None = None, stop: int | None = None) -> float:
    if init_val is None:
        ans = 0
        for x in iterable:
            ans = x
            break
    else:
        ans = init_val
    n_alpha = 1 - alpha
    if start is None and stop is None:
        for x in iterable:
            ans = n_alpha * ans + alpha * x
    else:
        start = start if start is not None else 0
        stop = stop if stop is not None else len(iterable)
        for i in range(start, stop):
            ans = n_alpha * ans + alpha * iterable[i]
    return ans
