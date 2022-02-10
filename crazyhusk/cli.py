"""Expose crazyhusk functionality to the commandline."""
# Standard Library
import argparse
import inspect
import logging
import sys

# Third Party
import pkg_resources


def set_subcommand_arguments(parser, command):
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

    if fullargs.defaults:
        firstdefault = len(fullargs.args) - len(fullargs.defaults)

    for i, arg in enumerate(fullargs.args):
        if fullargs.defaults and i >= firstdefault:
            default = fullargs.defaults[i - firstdefault]
            if default is None:
                parser.add_argument(dest=arg)
            elif type(default) is tuple or type(default) is list:
                parser.add_argument(
                    "--" + arg, default=default, type=type(default), nargs="+"
                )
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


def run():
    """Run the crazyhusk CLI entrypoint."""
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    commands_parser = parser.add_subparsers(
        title="subcommands", description="valid subcommands", help="subcommand help"
    )

    for entry_point in pkg_resources.iter_entry_points("crazyhusk.commands"):
        command = entry_point.load()
        if inspect.isfunction(command):
            cmd_parser = commands_parser.add_parser(entry_point.name)
            cmd_parser.set_defaults(command=command)
            set_subcommand_arguments(cmd_parser, command)

    args = parser.parse_args()
    if "command" in args:
        args.command(**{k: v for k, v in args.__dict__.items() if k != "command"})
