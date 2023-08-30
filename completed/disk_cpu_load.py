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
import logging
import getpass


@dataclass(frozen=True)
class ProcStat():
    """Dataclass container for /proc/stat file values
    NOTE: Class is frozen to be relatively immutable, but assignments to stats member is possible
    """

    stats: dict[str, list[int]]

    def get_total(self, stat_type: str) -> int:
        """Return the sum total of the array values for a given stat_type in self.stats

        Args:
            stat_type (str): name of stat in the self.stats dict

        Raises:
            KeyError if stat_type not in self.stats

        Returns:
            int: total sum of values for the given stat_type
        """
        try:
            values = self.stats[stat_type]
            logging.getLogger().debug("Summing values for '%s': %s", stat_type, values)
            return sum(values)
        except KeyError as error:
            logging.getLogger().error("The stats dict has no key '%s'", stat_type)
            raise error

    @staticmethod
    def current_stats() -> dict[str, list[int]]:
        """Static method to get current /proc/stat values as dict of stat type to list of int values

        Raises:
            FileNotFoundError if /proc/stat file does not exist
            PermissionError if executing user does not have permission to read /proc/stat

        Returns:
            dict[str, list[int]]: dict of stat type (e.g cpu, cpu0, intr) to list of int values
        """
        stats = dict()
        print(getpass.getuser())
        try:
            with open("/proc/stat", "r", encoding="UTF-8") as file:
                for line in file:
                    fields = line.split()
                    stat_type = fields[0]
                    stat_values = fields[1::]
                    stats[stat_type] = [int(stat) for stat in stat_values]
            return stats
        except FileNotFoundError as error:
            logging.getLogger().error("File /proc/stat not found, are you sure you're on Linux?")
            raise error
        except PermissionError as error:
            logging.getLogger().error(
                "Permission denied on file /proc/stat, check permissions for user '%s'.",
                getpass.getuser())
            raise error

    @classmethod
    def current(cls) -> "ProcStat":
        """Class method to return a ProcStat instance of the current /proc/stats state

        Returns:
            ProcStat: instance of ProcStat with the current /proc/stats state
        """
        stats = ProcStat.current_stats()
        return cls(stats)


def main():
    """Writes to disk and records CPU load using ProcStat to get /proc/stats states"""
    # Get parameters

    # Flush block device

    # Start disk read

    # Stop and calculate /proc/stat differences

    raise NotImplementedError


if __name__ == "__main__":
    main()
