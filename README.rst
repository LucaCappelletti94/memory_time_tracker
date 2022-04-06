Memory Time Tracker
=================================
|pip| |downloads|

Python tool to track the memory and time requirements of software.

Requirements
----------------------------
Please do note that this package makes use of `proc/meminfo <https://man7.org/linux/man-pages/man5/proc.5.html>`_,
so it is strictly compatible only with Linux systems.

As most tracker systems, this one works best if there is a limited amount of noise in the system.
Do not run other software while running the benchmark, or your results may be skewed.

Installing package
----------------------------
As usual, to install this package from Pypi just run:

.. code:: bash

    pip install memory_time_tracker


Usage example
---------------------------
You can use this package to track the execution of a given method as follows:

.. code:: python

    from memory_time_tracker import Tracker
    from time import sleep
    from tqdm.auto import trange
    import numpy as np
    import pandas as pd

    def example_function():
        arrays = []
        for i in trange(10, desc="Running test"):
            sleep(0.1)
            arrays.append(np.zeros((10000, 1000)))

    path = "/tmp/tracker.log"
            
    with Tracker(path):
        example_function()
    
    # The last line of the footer is used to mark whether
    # the execution was successfull or a crash happened 
    # and the logger died.
    df = pd.read_csv(
        path,
        skipfooter=1,
        engine="python"
    )


.. |pip| image:: https://badge.fury.io/py/memory-time-tracker.svg
    :target: https://badge.fury.io/py/memory-time-tracker
    :alt: Pypi project

.. |downloads| image:: https://pepy.tech/badge/memory-time-tracker
    :target: https://pepy.tech/badge/memory-time-tracker
    :alt: Pypi total project downloads 