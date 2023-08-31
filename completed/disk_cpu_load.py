#!/usr/bin/env python3
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
import os
import stat
from argparse import ArgumentParser, Namespace


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
            KeyError: if stat_type not in self.stats

        Returns:
            int: total sum of values for the given stat_type
        """
        try:
            values = self.stats[stat_type]
            logging.debug("Summing values for '%s': %s", stat_type, values)
            return sum(values)
        except KeyError as error:
            logging.error("The stats dict has no key '%s'", stat_type)
            raise error

    @staticmethod
    def current_stats() -> dict[str, list[int]]:
        """Static method to get current /proc/stat values as dict of stat type to list of int values

        Raises:
            FileNotFoundError: if /proc/stat file does not exist
            PermissionError: if executing user does not have permission to read /proc/stat

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
            logging.error(
                "File '/proc/stat' not found, are you sure you're on Linux?")
            raise error
        except PermissionError as error:
            logging.error(
                "Permission denied on file '/proc/stat', check permissions for user '%s'.",
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


def get_args() -> Namespace:
    """Configure and parse command line arguments, checking for valid inputs

    Raises:
        ArgumentTypeError: if any inputs are invalid

    Returns:
        Namespace: argparse.Namespace is simple wrapper object of parsed argument values
    """
    parser = ArgumentParser()
    parser.add_argument("-m", "--max-load", type=int,
                        default=30, help="Max acceptable CPU load as percent, default is 30")
    parser.add_argument("-x", "--xfer", type=int, default=4096,
                        help="Amount of data to read from disk in mebibytes, default is 4096")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="If present, produce more verbose output")
    parser.add_argument("device_filename", type=str,
                        help='This is the WHOLE-DISK device filename (with or without "/dev/")')
    args = parser.parse_args()
    # Set verbosity
    log_level = "DEBUG" if args.verbose else "WARNING"
    logging.basicConfig(level=log_level)
    logging.debug("--verbose is set to: %s", args.verbose)
    # Check max_load is greater than 0
    logging.debug("--max-load is set to: %s%%", args.max_load)
    if args.max_load < 0:
        logging.error("--max-load must be an integer greater than 0")
        exit(1)
    # Check xfer size is greater than 0
    logging.debug("--xfer size is set to: %sMiB", args.xfer)
    if args.xfer < 0:
        logging.error("--xfer must be an integer greater than 0")
        exit(1)
    # Warn if the device filename is not a block device
    logging.debug("device_filename is set to: %s", args.device_filename)
    try:
        file_mode = os.stat(args.device_filename).st_mode
        if not stat.S_ISBLK(file_mode):
            logging.warning("Device filename '%s' is not a block device.")
    except FileNotFoundError:
        logging.error(
            "File '%s' not found.", args.device_filename)
        exit(1)
    except PermissionError:
        logging.error(
            "Permission denied on file '%s', check permissions for user '%s'.",
            args.device_filename, getpass.getuser())
        exit(1)
    return args


def main():
    """Writes to disk and records CPU load using ProcStat to get /proc/stats states"""
    # Get parameters
    args = get_args()

    # Flush block device

    # Start disk read

    # Stop and calculate /proc/stat differences

    raise NotImplementedError


if __name__ == "__main__":
    main()
