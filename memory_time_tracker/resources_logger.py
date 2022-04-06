"""Submodule providing method to store the resources to memory or disk according to speed."""

from multiprocessing import Event
from time import sleep
from timeit import default_timer as timer

from .get_refresh_delay import get_refresh_delay
from .get_used_ram import get_used_ram


def resources_logger(stop: Event, path: str, calibration_offset: int = 0):
    """Worker that logs memory usage in a csv file until the stop event is set.

    Parameters
    ----------
    stop: mp.Event
        The stop signal that must be set to stop the ram logging.
    path: str
        The path of the csv where to log the data.
    calibration_offset: int = 0
        The optional system offsets to remove from the data that will be logged.
    """
    while stop.is_set():
        pass

    tracked = []
    tracked.append((0, get_used_ram() - calibration_offset))
    start = timer()
    last_delta = 0

    fp = open(path, "w")

    fp.write("delta,ram\n")

    while not stop.is_set():
        refresh_rate = get_refresh_delay(last_delta)
        sleep(refresh_rate)
        last_delta = timer() - start
        tracked.append((
            last_delta,
            get_used_ram() - calibration_offset,
        ))
        # If the refresh rate is bigger than 5 seconds
        # writing to file won't be a significant overhead.
        if refresh_rate > 5:
            while len(tracked):
                fp.write("{},{}\n".format(*tracked.pop(0)))
            fp.flush()
    for delta, ram in tracked:
        fp.write("{},{}\n".format(delta, ram))
    fp.flush()

    fp.write("0,0\n")

    fp.close()
