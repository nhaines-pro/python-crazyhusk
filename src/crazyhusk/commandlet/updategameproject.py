"""Wrapper object for UpdateGameProject commandlet."""

# Standard Library
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Optional

# CrazyHusk
from crazyhusk.commandlet.base import UnrealCommandlet

if TYPE_CHECKING:
    # CrazyHusk
    from crazyhusk.engine import UnrealEngine
    from crazyhusk.project import UnrealProject


class UpdateGameProjectError(Exception):
    """Custom exception representing errors encountered with UpdateGameProject."""


@dataclass
class UpdateGameProjectCommandlet(UnrealCommandlet):
    """Commandlet wrapper object for UpdateGameProject."""

    autocheckout: bool = False
    autosubmit: bool = False
    signsampleproject: bool = False
    category: Optional[str] = None
    changelistdescription: Optional[str] = None

    @property
    def name(self) -> str:
        """Get the commandlet name."""
        return "UpdateGameProject"

    def validate(self) -> None:
        """Raise exceptions if this instance is misconfigured."""
        if self.autosubmit and self.changelistdescription is None:
            raise UpdateGameProjectError(
                "To use autosubmit, changelist description must not be None."
            )
        if self.autosubmit and self.changelistdescription == "":
            raise UpdateGameProjectError(
                "To use autosubmit, changelist description must not be empty string."
            )
        return None

    def get_commandline_args(self) -> Iterable[str]:
        """Iterate strings of subprocess arguments to execute the commandlet."""
        if self.autocheckout:
            yield "-AutoCheckout"
        if self.autosubmit:
            yield "-AutoSubmit"
        if self.signsampleproject:
            yield "-SignSampleProject"

        if self.category is not None:
            yield f"-Category={self.category}"
        if self.changelistdescription is not None:
            yield f"-ChangelistDescription={self.changelistdescription}"

    def is_valid_for_engine(self, engine: UnrealEngine) -> bool:
        """Get whether this commandlet is available for a given Unreal engine."""
        return False

    def is_valid_for_project(self, project: UnrealProject) -> bool:
        """Get whether this commandlet is available for a given Unreal project."""
        return True
