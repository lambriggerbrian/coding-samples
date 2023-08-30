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
    """Dataclass container for /proc/stats file values"""
    stats: dict[str, list[int]]
    _raw_stats: list[str]

    def __init__(self, raw_stats: list[str] = None):
        """Initialize the raw_stats and compute totals from it

        Args:
            raw_stats (list[str], optional): stats to use, will get current stats if not passed.
                Defaults to None.
        """
        if raw_stats:
            self._raw_stats = raw_stats
        else:
            self._raw_stats = ProcStat.current_stats()
        self._process_stats()

    def _process_stats(self):
        """Populate self.stats dictionary from raw line values"""
        for line in self._raw_stats:
            fields = line.split()
            stat_type = fields[0]
            stat_values = fields[1::]
            self.stats[stat_type] = stat_values

    @staticmethod
    def current_stats() -> list[str]:
        """Static method to get current /proc/stats values as list of strings

        Raises:
            NotImplementedError: not yet implemented

        Returns:
            list[str]: list of the lines (as strings) read from current state of /proc/stats
        """
        raw_stats = []
        with open("/proc/stats", "r", encoding="UTF-8") as file:
            for line in file:
                raw_stats.append(line)

    @staticmethod
    def current() -> ProcStat:
        """Static method to return a ProcStat instance of the current /proc/stats state

        Raises:
            NotImplementedError: not yet implemented

        Returns:
            ProcStat: instance of ProcStat with the current /proc/stats state
        """
        return ProcStat(ProcStat.current_stats())


def main():
    """Writes to disk and records CPU load using ProcStat to get /proc/stats states"""
    raise NotImplementedError


if __name__ == "__main__":
    main()
