"""Object wrappers for working with Unreal Engine config files."""

# Standard Library
import configparser
import re

CONFIG_CATEGORIES = frozenset(
    [
        "Compat",
        "DeviceProfiles",
        "Editor",
        "EditorGameAgnostic",
        "EditorKeyBindings",
        "EditorLayout",
        "EditorPerProjectUserSettings",
        "EditorSettings",
        "Engine",
        "Game",
        "GameUserSettings",
        "Hardware",
        "Input",
        "InstallBundle",
        "Lightmass",
        "PakFileRules",
        "RuntimeOptions",
        "Scalability",
        "SourceControlSettings",
    ]
)


class UnrealConfigError(Exception):
    """Custom exception representing errors encountered with Unreal config files."""


class UnrealConfigParser(configparser.RawConfigParser):
    """Object wrapper representing a configuration stack."""

    RE_OPTION_SPECIALCHARS = re.compile(r"^([+-.!])")

    def __init__(self) -> None:
        """Initialize a new UnrealConfigParser."""
        super().__init__(strict=False)

    def optionxform(self, optionstr: str) -> str:
        """Transform the string used by ConfigParsers for use with key expression of options."""
        return UnrealConfigParser.RE_OPTION_SPECIALCHARS.sub("", optionstr)
