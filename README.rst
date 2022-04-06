Memory Time Tracker
=================================
|pip| |downloads|

Memory time tracker is a simple python tool to track the memory and time requirements of software across both very brief (milliseconds) and large (days) time and memory requirements through adaptative log resolution.

Tracking upwards to crash
------------------------------------
This package handles gracefully also use cases where the tracked software
dies because of OOM or generally crashes by adding a ``0,0`` as the last line of the CSV document
it produces when the execution finishes nominally while adding a ``-1,-1`` when the execution
finishes with a detectable exception. When there are crashes not detectable through exceptions,
such as machine freezes because of OOM, kernel panics or other things, neither ``0,0``nor ``1,1`` are (inevitably) written at the end of the CSV.

To help distinguish the different possible completion statuses, we have prepared three methods:

* ``has_completed_successfully`` to detect whether the execution has been completed without hiccups.
* ``has_crashed_gracefully`` to detect crashes that raised "normal" exceptions.
* ``has_crashed_ungracefully`` to detect crashes that did not raise "normal" exceptions, such as OOM and core dumps.

See more below in the Examples section.

Requirements
----------------------------
Please do note that this package makes use of `proc/meminfo <https://man7.org/linux/man-pages/man5/proc.5.html>`_,
so it is strictly compatible only with Linux systems.

Like most tracker systems, this one works best if there is a limited amount of noise in the system.
Do not run other software while running the benchmark, or your results may be skewed.

Installing package
----------------------------
As usual, to install this package from Pypi, just run:

.. code:: bash

    pip install memory_time_tracker


Usage example
---------------------------
You can use this package to track the execution of a given method as follows:

.. code:: python

    from memory_time_tracker import Tracker, has_completed_successfully, has_crashed_gracefully, has_crashed_ungracefully
    from time import sleep
    import pandas as pd

    def example_function():
        """Small example of function that takes 1 second."""
        for _ in range(10):
            sleep(0.1)

    # The path where we will store the log
    path = "/tmp/tracker.csv"

    # Create the tracker context
    with Tracker(path):
        example_function()

    print(
        "Successful: ", has_completed_successfully(path),
        "Crashed gracefully: ", has_crashed_gracefully(path),
        "Crashed ungracefully: ", has_crashed_ungracefully(path)
    )
        
    # We load in a pandas DataFrame the tracked performance.
    df = pd.read_csv(
        path,
        # The last line of the footer is used to mark whether
        # the execution was successful, or a crash happened 
        # and the logger died.
        skipfooter=1,
        # The skip footer option is only available when the engine
        # selected is Python
        engine="python"
    )

You can see this example `as a Jupyter Notebook here <https://github.com/LucaCappelletti94/memory_time_tracker/blob/main/Tracker%20tutorial.ipynb>`_ and `run it on Colab here <https://colab.research.google.com/drive/17RhQQyP8gmIb1qprQwOVPwut_mZgA01K?usp=sharing>`_.

Authors and License
---------------------------
This package was developed by `Luca Cappelletti <https://github.com/LucaCappelletti94>`_ and `Tommaso Fontana <https://github.com/zommiommy>`_ and is released under `MIT License <https://github.com/LucaCappelletti94/memory_time_tracker/blob/main/LICENSE>`_.

Future work
---------------------------
Since we have already developed a pipeline to draw performance diagrams comparing different 
libraries, we may integrate it within this library as it seems quite relevant.


.. |pip| image:: https://badge.fury.io/py/memory-time-tracker.svg
    :target: https://badge.fury.io/py/memory-time-tracker
    :alt: Pypi project

.. |downloads| image:: https://pepy.tech/badge/memory-time-tracker
    :target: https://pepy.tech/badge/memory-time-tracker
    :alt: Pypi total project downloads 