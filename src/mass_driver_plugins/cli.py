"""Command line entrypoint for mass-driver-plugins"""
import argparse
import sys
from typing import Optional

from mass_driver.discovery import discover_drivers


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    """Parse generic arguments, given as parameters"""
    parser = argparse.ArgumentParser(
        "mass-driver-plugins",
        description="Experimental plugin ecosystem for Mass Driver",
    )
    return parser.parse_args(arguments)


def cli(arguments: Optional[list[str]] = None):
    """Run the mass_driver_plugins cli"""
    if arguments is None:
        arguments = sys.argv[1:]
    parse_arguments(arguments)
    main()


def main():
    """Run the program's main command"""
    print("\n".join(discover_drivers()))
