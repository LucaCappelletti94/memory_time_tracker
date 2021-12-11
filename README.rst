Memory Time Tracker
=================================
Python tool to track the memory and time requirements of software.

Requirements
----------------------------
Please do note that this package makes use of [proc/meminfo](https://man7.org/linux/man-pages/man5/proc.5.html),
so it is strictly compatible only with Linux systems.

Installing package
----------------------------
We will publish this package relatively soon on Pypi, but for the time being you can install this by running:

.. code:: bash

    pip install -e git+https://github.com/LucaCappelletti94/memory_time_tracker.git

Usage example
---------------------------
You can use this package to track the execution of a given method as follows:

.. code:: python

    # TODO