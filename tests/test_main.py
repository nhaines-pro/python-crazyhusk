# Third Party
import pytest

# CrazyHusk
from crazyhusk import cli
from crazyhusk.__main__ import main


@pytest.mark.parametrize(
    "args,raises",
    [
        (None, (cli.CommandError, SystemExit, TypeError)),
        ([], (cli.CommandError, SystemExit)),
        (["test-command"], (cli.CommandError, SystemExit)),
        ([""], (cli.CommandError, SystemExit)),
        # TODO: monkeypatch pkg_resources behavior
    ],
)
def test_main(monkeypatch, args, raises):
    monkeypatch.setattr("sys.argv", args)
    if raises is not None:
        with pytest.raises(raises):
            assert main()
    else:
        assert main()
