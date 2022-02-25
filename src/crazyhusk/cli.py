"""Expose crazyhusk functionality to the commandline."""
# Standard Library
import argparse
import inspect
import logging
import sys
from typing import Any, List

try:
    # Standard Library
    from importlib.metadata import entry_points  # type:ignore
except ImportError:
    # Third Party
    from importlib_metadata import entry_points  # type:ignore


class CommandError(Exception):
    """Custom exception representing errors encountered with CLI."""


def set_subcommand_arguments(
    parser: argparse.ArgumentParser, command: Any
) -> argparse.ArgumentParser:
    """Dynamically set argparse.Parser subcommand arguments by inspecting a callable function."""
    if not isinstance(parser, argparse.ArgumentParser):
        raise TypeError(
            f"Parser provided must be of type argparse.ArgumentParser. Got: {parser!r}"
        )

    if not inspect.isfunction(command):
        raise TypeError(
            f"Command provided must be a callable function. Got:{command!r}"
        )

    fullargs = inspect.getfullargspec(command)
    if fullargs.defaults is not None:
        firstdefault = len(fullargs.args) - len(fullargs.defaults)

    for i, arg in enumerate(fullargs.args):
        if fullargs.defaults and i >= firstdefault:
            default = fullargs.defaults[i - firstdefault]
            if default is None:
                parser.add_argument(dest=arg)
            elif type(default) is tuple or type(default) is list:
                parser.add_argument("--" + arg, default=default, nargs="+")
            elif type(default) is bool and default:
                parser.add_argument(
                    "--disable_" + arg, dest=arg, default=default, action="store_false"
                )
            elif type(default) is bool and not default:
                parser.add_argument(
                    "--enable_" + arg, dest=arg, default=default, action="store_true"
                )
            else:
                parser.add_argument("--" + arg, default=default, type=type(default))
        else:
            parser.add_argument(dest=arg)

    return parser


def parse_cli_args(args: List[str]) -> argparse.Namespace:
    """Parse crazyhusk CLI arguments."""
    if args is None:
        raise CommandError("None is not parsable arguments.")
    elif len(args) == 0:
        raise CommandError("Must provide at least one argument.")

    parser = argparse.ArgumentParser()
    commands_parser = parser.add_subparsers(
        title="subcommands", description="valid subcommands", help="subcommand help"
    )

    for entry_point in entry_points().get("crazyhusk.commands", []):
        command = entry_point.load()
        if inspect.isfunction(command):
            cmd_parser = commands_parser.add_parser(entry_point.name)
            cmd_parser.set_defaults(command=command)
            set_subcommand_arguments(cmd_parser, command)

    return parser.parse_args(args)


def run(args: List[str] = sys.argv[1:]) -> None:
    """Run the crazyhusk CLI entrypoint."""
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    command_args = parse_cli_args(args)
    if "command" in command_args:
        command_args.command(
            **{k: v for k, v in command_args.__dict__.items() if k != "command"}
        )
