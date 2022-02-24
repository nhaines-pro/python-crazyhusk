# Standard Library
import configparser
from typing import Any

# Third Party
import pytest

# CrazyHusk
from crazyhusk import config


@pytest.fixture(scope="function")
def empty_parser() -> config.UnrealConfigParser:
    yield config.UnrealConfigParser()


def test_config_init(empty_parser:config.UnrealConfigParser) -> None:
    assert isinstance(empty_parser, configparser.RawConfigParser)


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
def test_config_optionxform(empty_parser:config.UnrealConfigParser, input_string:str, output_string:str) -> None:
    assert empty_parser.optionxform(input_string) == output_string
