"""Module providing the Tracker object."""
import multiprocessing as mp
import os
from time import sleep, time
from typing import List, Tuple

from statistics import mean, stdev
from environments_utils import is_linux

from .get_used_ram import get_used_ram
from .resources_logger import resources_logger


class Tracker:
    def __init__(
        self,
        file_name: str,
        end_delay: float = 4,
        calibrate: bool = True,
        calibration_seconds: float = 2,
        verbose: bool = False,
        start_delay: int = 5
    ):
        """Context manager that measure the time and ram a snipped of code use.

        Parameters
        ----------
        file_name: str,
            The csv file where the ram measurements will be logged.
        end_delay: float = 4,
            How much time the context manager will wait before exiting once
            the snipped has ended. This is used to measure the final ammount
            of ram used.
        calibrate: bool = True,
            If the context manager should do a calibration measurement before
            starting the code.
        calibration_seconds: float = 2,
            How much time, in seconds, the calibration step will take.
        verbose: bool = False,
            If the program should be verbose and print info or not.
        start_delay: int = 5,
            How much to wait before starting the tracker to let the process start.
        """

        if not is_linux():
            raise NotImplementedError(
                "The current implementation of the Tracker exclusively "
                "works on Linux systems."
            )

        self.end_delay = end_delay
        self.verbose = verbose
        self.stop = mp.Event()
        self.start_delay = start_delay
        self.file_name = file_name
        directory = os.path.dirname(file_name)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if verbose:
            print("Logging results into: {}".format(file_name))

        if calibrate:
            self.calibration_offset = self._calibrate(calibration_seconds)
        else:
            self.calibration_offset = 0

        self.process = mp.Process(
            target=resources_logger,
            args=[
                self.stop,
                file_name,
                self.calibration_offset
            ]
        )

    def _measure_ram(self, number_of_seconds: float) -> List[int]:
        """Returns a list of measurements

        Parameters
        ----------
            number_of_seconds: float,
                For how many seconds the function will measure the ram used
        """
        measurements = []
        start = time()
        while (time() - start) < number_of_seconds:
            measurements.append(get_used_ram())
            sleep(0.1)
        return measurements

    def _measure_mean_ram_usage(self, number_of_seconds: float) -> Tuple[float, float]:
        """Return the mean ram used in an interval of time.

        Parameters
        ----------
            number_of_seconds: float,
                For how many seconds the function will measure the ram used
        """
        measurements = self._measure_ram(number_of_seconds)
        return mean(measurements), stdev(measurements)

    def _calibrate(self, calibration_seconds: float) -> float:
        """Before letting python continue we take a couple of seconds to measure
            the ram in use before the program enters this context manager.

            This is used to get better measurements.

        Parameters
        ----------
            number_of_seconds: float,
                For how many seconds the function will measure the ram used
        """
        if self.verbose:
            print("Starting calibration")
        calibration_offset, calibration_std = self._measure_mean_ram_usage(
            calibration_seconds)
        if self.verbose:
            print("Calibration done, the mean ram used by the system is {} ± {} Gb ".format(
                calibration_offset, calibration_std))
        return calibration_offset

    def __enter__(self):
        self.stop.set()
        self.process.daemon = True
        self.process.start()
        sleep(self.start_delay)
        self.stop.clear()
        self.start_time = time()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.end_time = time()
        self.stop.set()
        self.process.join()

        if exc_type is not None:
            if self.verbose:
                print("The program had an exception %s" % str(exc_value))
            with open(self.file_name, "a") as f:
                f.write("-1,-1\n")

        end_ram, end_std = self._measure_mean_ram_usage(self.end_delay)
        if self.verbose:
            print("The ram used one che process finished is {} ± {} Gb".format(
                end_ram - self.calibration_offset, end_std))
            print("The process took {} seconds".format(
                self.end_time - self.start_time))
