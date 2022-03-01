# Standard Library
import argparse
import inspect
from typing import Any, List, Optional, Tuple, Type

# Third Party
import pytest

# CrazyHusk
from crazyhusk import cli


def test_set_subcommand_arguments_types() -> None:
    with pytest.raises(TypeError):
        cli.set_subcommand_arguments(None, None)

    with pytest.raises(TypeError):
        cli.set_subcommand_arguments(argparse.ArgumentParser(), None)

    def subcommand_noargs() -> None:
        pass

    assert isinstance(
        cli.set_subcommand_arguments(argparse.ArgumentParser(), subcommand_noargs),
        argparse.ArgumentParser,
    )

    def subcommand_nodefaults(arg: Any) -> None:
        pass

    assert isinstance(
        cli.set_subcommand_arguments(argparse.ArgumentParser(), subcommand_nodefaults),
        argparse.ArgumentParser,
    )

    def subcommand_default_none(arg: Optional[Any] = None) -> None:
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_none
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_tuple(arg: Any = ()) -> None:
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_tuple
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_list(arg: Any = []) -> None:
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_list
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_true(arg: Any = True) -> None:
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_true
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_false(arg: Any = False) -> None:
        pass

    assert isinstance(
        cli.set_subcommand_arguments(
            argparse.ArgumentParser(), subcommand_default_false
        ),
        argparse.ArgumentParser,
    )

    def subcommand_default_string(arg: Any = "") -> None:
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
        (["test"], None),
    ],
)
def test_parse_cli_args(
    args: Optional[List[str]],
    raises: Optional[Type[BaseException]],
    monkeypatch: Any,
    test_entry_point: Any,
) -> None:
    monkeypatch.setattr(
        cli, "entry_points", lambda: {"crazyhusk.commands": [test_entry_point]}
    )
    if raises is not None:
        with pytest.raises(raises):
            assert cli.parse_cli_args(args)
    else:
        parsed = cli.parse_cli_args(args)
        assert isinstance(parsed, argparse.Namespace)
        assert "command" in parsed
        assert inspect.isfunction(parsed.command)


def test_parse_cli_args_entry_points(
    monkeypatch: Any, test_entry_point: Any, null_entry_point: Any
) -> None:
    monkeypatch.setattr(
        cli, "entry_points", lambda: {"crazyhusk.commands": [test_entry_point]}
    )
    args = cli.parse_cli_args(["test"])
    assert isinstance(args, argparse.Namespace)
    assert "command" in args

    monkeypatch.setattr(
        cli, "entry_points", lambda: {"crazyhusk.commands": [null_entry_point]}
    )
    with pytest.raises(SystemExit):
        assert cli.parse_cli_args(["test"]) is None


@pytest.mark.parametrize(
    "args,raises",
    [
        (None, (cli.CommandError, SystemExit)),
        ([], (cli.CommandError, SystemExit)),
        (["test-command"], (cli.CommandError, SystemExit)),
        ([""], (cli.CommandError, SystemExit)),
        (["test"], None),
    ],
)
def test_cli_run(
    args: Optional[List[str]],
    raises: Optional[Tuple[Type[BaseException]]],
    monkeypatch: Any,
    test_entry_point: Any,
) -> None:
    monkeypatch.setattr(
        cli, "entry_points", lambda: {"crazyhusk.commands": [test_entry_point]}
    )
    if raises is not None:
        with pytest.raises(raises):
            assert cli.run(args) is None
    else:
        assert cli.run(args) is None


def test_cli_run_entry_points(monkeypatch: Any, test_entry_point: Any) -> None:
    monkeypatch.setattr(
        cli, "entry_points", lambda: {"crazyhusk.commands": [test_entry_point]}
    )
    assert cli.run(["test"]) is None
