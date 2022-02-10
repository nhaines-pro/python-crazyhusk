# Standard Library
import argparse

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
