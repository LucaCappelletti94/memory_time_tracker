Memory Time Tracker
=================================
Python tool to track the memory and time requirements of software.

Requirements
----------------------------
Please do note that this package makes use of [proc/meminfo](https://man7.org/linux/man-pages/man5/proc.5.html),
so it is strictly compatible only with Linux systems.

As most tracker systems, this one works best if there is a limited amount of noise in the system.
Do not run other software while running the benchmark, or your results may be skewed.

Installing package
----------------------------
We will publish this package relatively soon on Pypi, but for the time being you can install this by running:

.. code:: bash

    pip install -e git+https://github.com/LucaCappelletti94/memory_time_tracker.git

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
        
    df = pd.read_csv(
        path,
        skipfooter=1,
        engine="python"
    )