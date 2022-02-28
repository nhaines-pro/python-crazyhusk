"""Wrapper objects for Unreal Engine builds."""

# Future Standard Library
from __future__ import annotations

# Standard Library
import platform
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Iterable, Optional

if TYPE_CHECKING:
    # CrazyHusk
    from crazyhusk.engine import UnrealEngine


class Buildable(ABC):
    @abstractmethod
    def is_buildable(self) -> bool:
        ...

    @abstractmethod
    def get_build_command(
        self,
        target: Optional[str] = None,
        configuration: Optional[str] = None,
        platform: Optional[str] = None,
        *extra_switches: str,
        **extra_parameters: str,
    ) -> Iterable[str]:
        ...

    @property
    @abstractmethod
    def engine(self) -> Optional[UnrealEngine]:
        ...

    def is_valid_build_target(self, target: str) -> bool:
        return target in {"Game", "Editor", "Server"}

    def is_valid_build_platform(self, platform: str) -> bool:
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
        return configuration in {
            "Debug",
            "DebugGame",
            "Development",
            "Shipping",
            "Test",
        }

    def default_local_platform(self) -> str:
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
        return "Editor"

    def default_build_configuration(self) -> str:
        return "Development"


class UnrealBuild(object):
    buildable: Buildable
    __target: str
    __configuration: str
    __platform: str

    def __init__(
        self,
        buildable: Buildable,
        target: Optional[str] = None,
        configuration: Optional[str] = None,
        build_platform: Optional[str] = None,
    ) -> None:
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

    @property
    def target(self) -> str:
        return self.__target

    @target.setter
    def target(self, value: str) -> None:
        if self.buildable.is_valid_build_target(value):
            self.__target = value

    @property
    def configuration(self) -> str:
        return self.__configuration

    @configuration.setter
    def configuration(self, value: str) -> None:
        if self.buildable.is_valid_build_configuration(value):
            self.__configuration = value

    @property
    def platform(self) -> str:
        return self.__platform

    @platform.setter
    def platform(self, value: str) -> None:
        if self.buildable.is_valid_build_platform(value):
            self.__platform = value

    def run(
        self,
        *extra_switches: str,
        **extra_parameters: str,
    ) -> int:
        if not self.buildable.is_buildable():
            raise ValueError(f"Buildable: {self.buildable!r} cannot be built.")

        if self.buildable.engine is None:
            raise ValueError(
                f"Buildable: {self.buildable!r} could not resolve a valid UnrealEngine."
            )

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
