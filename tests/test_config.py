# Standard Library
import configparser

# Third Party
import pytest

# CrazyHusk
from crazyhusk import config


@pytest.fixture(scope="function")
def empty_parser():
    yield config.UnrealConfigParser()


def test_config_init(empty_parser):
    assert isinstance(empty_parser, configparser.RawConfigParser)
    assert empty_parser._strict is False


@pytest.mark.parametrize(
    "input_string,output_string",
    [
        ("AxisConfig", "AxisConfig"),
        ("+AxisConfig", "AxisConfig"),
        ("-AxisConfig", "AxisConfig"),
        (".AxisConfig", "AxisConfig"),
        ("!AxisConfig", "AxisConfig"),
    ],
)
def test_config_optionxform(empty_parser, input_string, output_string):
    assert empty_parser.optionxform(input_string) == output_string
