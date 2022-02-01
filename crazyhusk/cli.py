"""Expose crazyhusk functionality to the commandline."""
import argparse
import logging
import sys

import pkg_resources


def run():
    """Run the crazyhusk CLI entrypoint."""
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    commands_parser = parser.add_subparsers(help="sub-command help", dest="command")

    commands = {}
    for entry_point in pkg_resources.iter_entry_points("crazyhusk.commands"):
        commands[entry_point.name] = entry_point.load()
        commands_parser.add_parser(entry_point.name)

    args = parser.parse_args()

    command = commands.get(args.command)
    if command is not None:
        command()
