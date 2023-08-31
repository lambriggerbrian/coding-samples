#!/usr/bin/env python3
"""Script to test CPU load imposed by a simple disk read operation

Adapted from disk_cpu_load.sh by Rod Smith <rod.smith@canonical.com>

Authors:
    Brian Lambrigger <lambrigger.brian@gmail.com>

The purpose of this script is to run disk stress tests by recording /proc/stats
values before and after a disk read.

Usage:
  disk_cpu_load.py [-h] [-m MAX_LOAD] [-b BLOCK_SIZE] [-x XFER] [-v] device_filename

Parameters:
 -m/--max-load <load>     -- The maximum acceptable CPU load, as a percentage.
                             Defaults to 30.
 -b/--block-size <bytes>  -- Amount of data to read at a time in bytes.
                             Defaults to 1048576 (1 MiB)
 -x/--xfer                -- The number of blocks to read from the disk.
                             Total size read will be block-size * xfer.
                             Defaults to 4096 (4 GiB).
 --verbose                -- If present, produce more verbose output
 <device-filename>        -- This is the WHOLE-DISK device filename (with or
                             without "/dev/"), e.g. "sda" or "/dev/sda". The
                             script finds a filesystem on that device, mounts
                             it if necessary, and runs the tests on that mounted filesystem. 
                             Defaults to /dev/sda.
"""
import getpass
import logging
import os
import re
import stat
import subprocess
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass


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
            logging.error("The stats dict has no key: '%s'", stat_type)
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
        try:
            with open("/proc/stat", "r", encoding="UTF-8") as file:
                for line in file:
                    fields = line.split()
                    # First element of the line is the type of values (e.g. cpu, intr)
                    stat_type = fields[0]
                    # Remaining elements are the values of different fields
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
    parser.add_argument("-b", "--block-size", type=int, default=1048576,
                        help="Amount of data to read at a time in bytes, default is 1048576")
    parser.add_argument("-x", "--xfer", type=int, default=4096,
                        help="Number of blocks to read from disk, default is 4096")
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

    # Check block size is greater than 0
    logging.debug("--block-size is set to: %sB", args.block_size)
    if args.block_size < 0:
        logging.error(
            "--block-size must be an integer greater than 0.")
        exit(1)

    # Check xfer size is greater than 0
    logging.debug("--xfer size is set to: %s", args.xfer)
    if args.xfer < 0:
        logging.error("--xfer must be an integer greater than 0.")
        exit(1)

    # Sanitize device filename for missing /dev/ prefix
    initial_device = args.device_filename
    if not re.search("^/dev/", initial_device):
        args.device_filename = f"/dev/{initial_device}"

    # Check if the device filename is not a block device
    logging.debug("device_filename is set to: %s", args.device_filename)
    try:
        file_mode = os.stat(args.device_filename).st_mode
        if not stat.S_ISBLK(file_mode):
            logging.error("Device filename '%s' is not a block device.")
            exit(1)
    except FileNotFoundError:
        logging.error(
            "File '%s' not found.", args.device_filename)
        exit(1)
    except PermissionError:
        logging.error(
            "Permission denied on file '%s', check permissions for user '%s' on device '%s'.",
            args.device_filename, getpass.getuser(), args.device_filename)
        exit(1)
    return args


def main():
    """Writes to disk and records CPU load using ProcStat to get /proc/stats states"""
    # Get parameters
    args = get_args()
    disk_device = args.device_filename
    max_load = args.max_load
    block_size = args.block_size
    xfer_size = args.xfer

    # Flush block device
    logging.debug("Flushing buffers for device '%s'.", disk_device)
    try:
        subprocess.run(["blockdev", "--flushbufs", disk_device], check=True)
    except subprocess.CalledProcessError:
        logging.error("Could not flush buffers on device '%s', you may need to execute as root.",
                      disk_device)
        exit(1)

    # Record initial /proc/stat values
    init_stats = ProcStat.current()

    # Start disk read
    logging.debug("Beginning read of '%s' (size %sMiB)",
                  disk_device, xfer_size)
    subprocess.run(["dd", f"if={disk_device}", "of=/dev/null", f"bs={block_size}",
                   f"count={xfer_size}"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logging.debug("Read complete!")

    # Stop and calculate /proc/stat differences
    end_stats = ProcStat.current()

    # Calculate totals and differences
    init_total = init_stats.get_total("cpu")
    logging.debug("Start CPU time = %s", init_total)

    end_total = end_stats.get_total("cpu")
    logging.debug("End CPU time = %s", end_total)

    diff_idle = end_stats.stats["cpu"][3] - init_stats.stats["cpu"][3]
    diff_total = end_total - init_total
    diff_used = diff_total - diff_idle
    logging.debug("CPU time used: %s", diff_used)
    logging.debug("Total elapsed time = %s", diff_total)

    # Calculate total load and Pass/Fail
    cpu_load = 0
    if diff_total != 0:
        cpu_load = (diff_used*100)/diff_total
    print(f"Detected CPU load is {cpu_load}%")
    if cpu_load > max_load:
        print("*** DISK CPU LOAD TEST HAS FAILED! ***")
        exit(1)


if __name__ == "__main__":
    main()
