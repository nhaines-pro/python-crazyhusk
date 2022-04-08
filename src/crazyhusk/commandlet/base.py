"""Wrapper objects for Unreal Engine commandlets."""

# Standard Library
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    # CrazyHusk
    from crazyhusk.engine import UnrealEngine
    from crazyhusk.project import UnrealProject


class UnrealCommandlet(ABC):
    """Base class for working with Unreal commandlets."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the commandlet name."""
        raise NotImplementedError()

    @abstractmethod
    def validate(self) -> None:
        """Raise exceptions if this instance is misconfigured."""
        raise NotImplementedError()

    @abstractmethod
    def get_commandline_args(self) -> Iterable[str]:
        """Iterate strings of subprocess arguments to execute the commandlet."""
        raise NotImplementedError()

    @abstractmethod
    def is_valid_for_engine(self, engine: UnrealEngine) -> bool:
        """Get whether this commandlet is available for a given Unreal engine."""
        raise NotImplementedError()

    @abstractmethod
    def is_valid_for_project(self, project: UnrealProject) -> bool:
        """Get whether this commandlet is available for a given Unreal project."""
        raise NotImplementedError()
