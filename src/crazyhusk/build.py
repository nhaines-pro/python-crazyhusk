"""Wrapper objects for Unreal Engine builds."""

# Future Standard Library
from __future__ import annotations

# Standard Library
import platform
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable, Optional

if TYPE_CHECKING:
    # CrazyHusk
    from crazyhusk.engine import UnrealEngine


class Buildable(ABC):
    """Abstract base class for objects buildable by Unreal's build tools."""

    @abstractmethod
    def is_buildable(self) -> bool:
        """Get whether this object is buildable in its current configuration."""
        raise NotImplementedError()

    @abstractmethod
    def get_build_command(
        self,
        target: Optional[str] = None,
        configuration: Optional[str] = None,
        platform: Optional[str] = None,
        *extra_switches: str,
        **extra_parameters: str,
    ) -> Iterable[str]:
        """Iterate strings of subprocess arguments to execute the build."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def engine(self) -> Optional[UnrealEngine]:
        """Get the associated UnrealEngine object for this Buildable."""
        raise NotImplementedError()

    def is_valid_build_target(self, target: str) -> bool:
        """Get whether a given build target is valid for this Buildable."""
        return target in {"Game", "Editor", "Server"}

    def is_valid_build_platform(self, platform: str) -> bool:
        """Get whether a given platform is valid for this Buildable."""
        return platform in {
            "Win32",
            "Win64",
            "Linux",
            "LinuxAArch64",
            "Mac",
            "Android",
            "IOS",
        }

    def is_valid_build_configuration(self, configuration: str) -> bool:
        """Get whether a given build configuration is valid for this Buildable."""
        return configuration in {
            "Debug",
            "DebugGame",
            "Development",
            "Shipping",
            "Test",
        }

    def is_valid_static_analyzer(self, static_analyzer: str) -> bool:
        """Get whether a given c++ static analyzer is valid for this Buildable."""
        return platform.system() == "Windows" and static_analyzer in {
            "VisualCpp",
            "PVSStudio",
        }

    def default_local_platform(self) -> str:
        """Get the default build platform for the local system."""
        local_system = platform.system()
        if local_system == "Windows":
            return "Win64"
        elif local_system == "Linux":
            return "Linux"
        elif local_system == "Darwin":
            return "Mac"
        raise NotImplementedError(
            f"Default build platform for {local_system} not defined."
        )

    def default_build_target(self) -> str:
        """Get the default build target for this Buildable."""
        return "Editor"

    def default_build_configuration(self) -> str:
        """Get the default build configuration for this Buildable."""
        return "Development"


class UnrealBuild(object):
    """Object wrapper for composing and running an Unreal build subroutine."""

    buildable: Buildable
    __target: str
    __configuration: str
    __platform: str
    __static_analyzer: Optional[str]

    def __init__(
        self,
        buildable: Buildable,
        target: Optional[str] = None,
        configuration: Optional[str] = None,
        build_platform: Optional[str] = None,
        static_analyzer: Optional[str] = None,
    ) -> None:
        """Initialize a new UnrealBuild."""
        self.buildable = buildable
        if target is None:
            self.target = self.buildable.default_build_target()
        else:
            self.target = target

        if configuration is None:
            self.configuration = self.buildable.default_build_configuration()
        else:
            self.configuration = configuration

        if build_platform is None:
            self.platform = self.buildable.default_local_platform()
        else:
            self.platform = build_platform

        self.static_analyzer = static_analyzer

    @property
    def target(self) -> str:
        """Get the build target for this UnrealBuild."""
        return self.__target

    @target.setter
    def target(self, value: str) -> None:
        """Set the build target for this UnrealBuild."""
        if self.buildable.is_valid_build_target(value):
            self.__target = value

    @property
    def configuration(self) -> str:
        """Get the build configuration for this UnrealBuild."""
        return self.__configuration

    @configuration.setter
    def configuration(self, value: str) -> None:
        """Set the build configuration for this UnrealBuild."""
        if self.buildable.is_valid_build_configuration(value):
            self.__configuration = value

    @property
    def platform(self) -> str:
        """Get the build platform for this UnrealBuild."""
        return self.__platform

    @platform.setter
    def platform(self, value: str) -> None:
        """Set the build platform for this UnrealBuild."""
        if self.buildable.is_valid_build_platform(value):
            self.__platform = value

    @property
    def static_analyzer(self) -> Optional[str]:
        """Get the c++ static analyzer platform for this UnrealBuild."""
        return self.__static_analyzer

    @static_analyzer.setter
    def static_analyzer(self, value: Optional[str]) -> None:
        """Set the c++ static analyzer platform for this UnrealBuild."""
        if value is None:
            self.__static_analyzer = None
        elif self.buildable.is_valid_static_analyzer(value):
            self.__static_analyzer = value

    def run(
        self,
        *extra_switches: str,
        **extra_parameters: str,
    ) -> int:
        """Execute the currently configured build subprocess for this UnrealBuild."""
        if not self.buildable.is_buildable():
            raise ValueError(f"Buildable: {self.buildable!r} cannot be built.")

        if self.buildable.engine is None:
            raise ValueError(
                f"Buildable: {self.buildable!r} could not resolve a valid UnrealEngine."
            )

        if self.static_analyzer is not None:
            extra_parameters["StaticAnalyzer"] = self.static_analyzer

        with self.buildable.engine:
            return self.buildable.engine.run(
                *self.buildable.get_build_command(
                    self.target,
                    self.configuration,
                    self.platform,
                    *extra_switches,
                    **extra_parameters,
                ),
                expected_retcodes={0, 2},
            )
