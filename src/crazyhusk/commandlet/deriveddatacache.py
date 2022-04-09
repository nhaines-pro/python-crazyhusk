"""Wrapper object for DerivedDataCache commandlet."""

# Standard Library
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, List, Optional

# CrazyHusk
from crazyhusk.commandlet.base import UnrealCommandlet

if TYPE_CHECKING:
    # CrazyHusk
    from crazyhusk.engine import UnrealEngine
    from crazyhusk.project import UnrealProject


class DerivedDataCacheError(Exception):
    """Custom exception representing errors encountered with DerivedDataCache."""


@dataclass
class DerivedDataCacheCommandlet(UnrealCommandlet):
    """Commandlet wrapper object for DerivedDataCache."""

    fill: bool = False
    startuponly: bool = False
    mapsonly: bool = False
    projectonly: bool = False
    dev: bool = False
    noredist: bool = False
    subsetmod: Optional[int] = None
    subsettarget: Optional[int] = None
    maps: List[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        """Get the commandlet name."""
        return "DerivedDataCache"

    def validate(self) -> None:
        """Raise exceptions if this instance is misconfigured."""
        return None

    def get_commandline_args(self) -> Iterable[str]:
        """Iterate strings of subprocess arguments to execute the commandlet."""
        if self.fill:
            yield "-FILL"
        if self.startuponly:
            yield "-STARTUPONLY"
        if self.mapsonly:
            yield "-MAPSONLY"
        if self.projectonly:
            yield "-PROJECTONLY"
        if self.dev:
            yield "-DEV"
        if self.noredist:
            yield "-NOREDIST"

        if self.subsetmod is not None:
            yield f"-SubsetMod={self.subsetmod}"
        if self.subsettarget is not None:
            yield f"-SubsetTarget={self.subsettarget}"

        if len(self.maps) > 0:
            yield f"-Map={'+'.join(self.maps)}"

    def is_valid_for_engine(self, engine: UnrealEngine) -> bool:
        """Get whether this commandlet is available for a given Unreal engine."""
        return True

    def is_valid_for_project(self, project: UnrealProject) -> bool:
        """Get whether this commandlet is available for a given Unreal project."""
        return True
