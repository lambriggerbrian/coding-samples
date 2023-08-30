#!/usr/bin/env python
"""Script to test CPU load imposed by a simple disk read operation

Adapted from disk_cpu_load.sh by Rod Smith <rod.smith@canonical.com>

Authors:
    Brian Lambrigger <lambrigger.brian@gmail.com>

The purpose of this script is to run disk stress tests using the
stress-ng program.
Usage:
  disk_cpu_load.py [ --max-load <load> ] [ --xfer <mebibytes> ]
                   [ --verbose ] [ <device-filename> ]

Parameters:
 --max-load <load> -- The maximum acceptable CPU load, as a percentage.
                      Defaults to 30.
 --xfer <mebibytes> -- The amount of data to read from the disk, in
                       mebibytes. Defaults to 4096 (4 GiB).
 --verbose -- If present, produce more verbose output
 <device-filename> -- This is the WHOLE-DISK device filename (with or
                      without "/dev/"), e.g. "sda" or "/dev/sda". The
                      script finds a filesystem on that device, mounts
                      it if necessary, and runs the tests on that mounted
                      filesystem. Defaults to /dev/sda.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcStat():
    """Dataclass container for /proc/stat file values"""
    stats: dict[str, list[int]]

    @staticmethod
    def current_stats() -> dict[str, list[int]]:
        """Static method to get current /proc/stat values as dict of stat type to list of int values

        Raises:
            NotImplementedError: not yet implemented

        Returns:
            dict[str, list[int]]: dict of stat type (e.g cpu, cpu0, intr) to list of int values
        """
        stats = dict()
        with open("/proc/stat", "r", encoding="UTF-8") as file:
            for line in file:
                fields = line.split()
                stat_type = fields[0]
                stat_values = fields[1::]
                stats[stat_type] = stat_values
        return stats

    @classmethod
    def current(cls) -> "ProcStat":
        """Class method to return a ProcStat instance of the current /proc/stats state

        Raises:
            NotImplementedError: not yet implemented

        Returns:
            ProcStat: instance of ProcStat with the current /proc/stats state
        """
        stats = ProcStat.current_stats()
        return cls(stats)


def main():
    """Writes to disk and records CPU load using ProcStat to get /proc/stats states"""
    raise NotImplementedError


if __name__ == "__main__":
    main()
