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

    for param in inspect.signature(command).parameters.values():
        vargs = []
        kwargs = {}

        if param.default is not inspect.Parameter.empty:
            kwargs["default"] = param.default

        name = param.name
        if param.kind == inspect.Parameter.POSITIONAL_ONLY:
            pass
        elif param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            if param.default is not inspect.Parameter.empty:
                name = f"--{param.name}"
                kwargs["dest"] = param.name
        elif param.kind == inspect.Parameter.VAR_POSITIONAL:
            kwargs["nargs"] = argparse.ZERO_OR_MORE
        elif param.kind == inspect.Parameter.KEYWORD_ONLY:
            if param.default is not inspect.Parameter.empty:
                name = f"--{param.name}"
                kwargs["dest"] = param.name
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            pass
        else:
            raise TypeError(f"Invalid function signature parameter type: {param.kind}")

        if type(param.default) is bool:
            if param.default:
                name = f"--disable-{param.name}"
                kwargs["dest"] = param.name
                kwargs["action"] = "store_false"
            else:
                name = f"--enable-{param.name}"
                kwargs["dest"] = param.name
                kwargs["action"] = "store_true"

        vargs.append(name)
        parser.add_argument(*vargs, **kwargs)
    return parser


def parse_cli_args(args: List[str]) -> argparse.Namespace:
    """Parse crazyhusk CLI arguments."""
    if args is None:
        raise CommandError("None is not parsable arguments.")
    elif len(args) == 0:
        raise CommandError("Must provide at least one argument.")

    parser = argparse.ArgumentParser()
    commands_parser = parser.add_subparsers(title="subcommands")

    for entry_point in entry_points().get("crazyhusk.commands", []):
        command = entry_point.load()
        if inspect.isfunction(command):
            docstring = inspect.getdoc(command)
            if docstring is not None:
                docstring = docstring.split("\n")[0]
            cmd_parser = commands_parser.add_parser(entry_point.name, help=docstring)
            cmd_parser.set_defaults(command=command)
            set_subcommand_arguments(cmd_parser, command)

    return parser.parse_args(args)


def run(args: List[str] = sys.argv[1:]) -> None:
    """Run the crazyhusk CLI entrypoint."""
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    command_args = parse_cli_args(args)
    if "command" in command_args:
        vargs = []
        kwargs = {}
        for param in inspect.signature(command_args.command).parameters.values():
            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                vargs.append(getattr(command_args, param.name))
            elif param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                vargs.append(getattr(command_args, param.name))
            elif param.kind == inspect.Parameter.VAR_POSITIONAL:
                vargs.extend(getattr(command_args, param.name))
            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                kwargs[param.name] = getattr(command_args, param.name)
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                pass
            else:
                raise TypeError(
                    f"Invalid function signature parameter type: {param.kind}"
                )
        command_args.command(*vargs, **kwargs)
