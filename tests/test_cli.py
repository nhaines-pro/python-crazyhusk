# Standard Library
import argparse
import inspect

# Third Party
import pytest

# CrazyHusk
from crazyhusk import cli


def test_set_subcommand_arguments_types():
    with pytest.raises(TypeError):
        cli.set_subcommand_arguments(None, None)

    with pytest.raises(TypeError):
        cli.set_subcommand_arguments(argparse.ArgumentParser(), None)

    def subcommand_noargs():
        pass

    assert isinstance(
        cli.set_subcommand_arguments(argparse.ArgumentParser(), subcommand_noargs),
        argparse.ArgumentParser,
    )

    def subcommand_nodefaults(arg):
        pass

    assert isinstance(
        cli.set_subcommand_arguments(argparse.ArgumentParser(), subcommand_nodefaults),
        argparse.ArgumentParser,
    )

    def subcommand_default_none(arg=None):
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_none
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_tuple(arg=()):
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_tuple
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_list(arg=[]):
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_list
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_true(arg=True):
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_true
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_false(arg=False):
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_false
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_string(arg=""):
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_string
        ),
        argparse.ArgumentParser,
    )


@pytest.mark.parametrize(
    "args,raises",
    [
        (None, cli.CommandError),
        ([], cli.CommandError),
        (["test-command"], SystemExit),
        ([""], SystemExit),
        # TODO: monkeypatch pkg_resources behavior
    ],
)
def test_parse_cli_args(args, raises):
    if raises is not None:
        with pytest.raises(raises):
            assert cli.parse_cli_args(args)
    else:
        args = cli.parse_cli_args(args)
        assert isinstance(args, argparse.Namespace)
        assert "command" in args
        assert inspect.isfunction(args.command)


@pytest.mark.parametrize(
    "args,raises",
    [
        (None, (cli.CommandError, SystemExit)),
        ([], (cli.CommandError, SystemExit)),
        (["test-command"], (cli.CommandError, SystemExit)),
        ([""], (cli.CommandError, SystemExit)),
        # TODO: monkeypatch pkg_resources behavior
    ],
)
def test_parse_cli_run(args, raises):
    if raises is not None:
        with pytest.raises(raises):
            assert cli.run(args)
    else:
        assert cli.run(args)
