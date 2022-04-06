"""Submodule providing methods to measure the current RAM usage."""


def get_used_ram():
    """Return the ammout of ram used **BY THE SYSTEM**.

    Note that the amount is returned in GB.

    The values are read from /proc/meminfo (LINUX ONLY) to be as close as precise
    as possible. Moreover, the ram used is computed by:

    MemTotal - MemFree - Buffers - Cached - Slab

    Where:
        - MemTotal is the total ammount of ram connected to the motherboard.
        - MemFree is the total ammout of ram free.
        - Buffers is the ammount of ram used for I/O buffers such as disks and
            sockets (This is supposed to be < 20Mb).
        - Cached is the total ammount of ram used for caching. This is used to
            save the dirty pages of memory before they are synced with the disk
            and for the ramdisks.
        - Slab is the total ammount of ram used by the kernel.
    More infos at https://man7.org/linux/man-pages/man5/proc.5.html

    All of this is done to try to remove as much as possibles any system bias.
    """
    # Read the memory statistics
    with open("/proc/meminfo") as f:
        txt = f.read()

    # Convert the file into a dictionary with all the metrics
    data = {
        k: int(v.strip()[:-2])
        if v.lower().endswith("b")
        else int(v.strip())
        for (k, v) in [
            x.split(":")
            for x in txt.split("\n")
            if x.strip() != ""
        ]
    }
    # Total ram - Free Ram - Disks and sockets buffers - cache - kernel used memory
    return (data["MemTotal"] - data["MemFree"] - data["Buffers"] - data["Cached"] - data["Slab"]) / (1024**2)
