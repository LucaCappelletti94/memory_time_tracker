"""Submodule providing heuristic for the amount of time to wait to store info."""


def get_refresh_delay(elapsed: float) -> float:
    """Returns delay to wait for to store info.
    
    The main goal of this method is to avoid to have too low resolution
    in the very fast benchmarks, while not having gigantic log files
    in the very slow benchmarks.

    Parameters
    ----------------------------
    elapsed: float
        The amoount of time that has elapsed so far.

    Returns
    ----------------------------
    Amount of time to be waited before next log entry.
    """
    if elapsed < 0.01:
        return 0
    if elapsed < 0.1:
        return 0.00001
    if elapsed < 1:
        return 0.01
    if elapsed < 10:
        return 0.1
    if elapsed < 60:
        return 1
    if elapsed < 60*10:
        return 30
    if elapsed < 60*60:
        return 60
    return 60*3
