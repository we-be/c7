# noinspection PyBroadException
import time
from typing import Callable


def retry(f: Callable, n: int, t=1, _i=0):
    """
    :params:
    f: parameterless function to retry
    n: number of times to retry before throwing
    t: time to sleep (in seconds) between retries
    _i: do not use this
    """
    try:
        _i += 1
        f()
    except Exception as e:
        if _i > n:
            raise e
        time.sleep(t)
        retry(f, n, t, _i)