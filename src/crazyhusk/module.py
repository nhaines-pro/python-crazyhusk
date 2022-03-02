"""Wrapper objects for Unreal code modules."""

# Future Standard Library
from __future__ import annotations

# Standard Library
from typing import Any, Dict, List, Optional, Union

__all__ = ["ModuleDescriptor"]

HOST_TYPES = frozenset(
    {
        "Runtime",
        "RuntimeNoCommandlet",
        "RuntimeAndProgram",
        "CookedOnly",
        "UncookedOnly",
        "Developer",
        "DeveloperTool",
        "Editor",
        "EditorNoCommandlet",
        "EditorAndProgram",
        "Program",
        "ServerOnly",
        "ClientOnly",
        "ClientOnlyNoCommandlet",
    }
)

LOADING_PHASES = frozenset(
    {
        "EarliestPossible",
        "PostConfigInit",
        "PostSplashScreen",
        "PreEarlyLoadingScreen",
        "PreLoadingScreen",
        "PreDefault",
        "Default",
        "PostDefault",
        "PostEngineInit",
        "None",
    }
)


class ModuleDescriptor(object):
    """Object wrapper representation of Unreal code module, equivalent to FModuleDescriptor.

    https://docs.unrealengine.com/en-US/API/Runtime/Projects/FModuleDescriptor/index.html
    """

    def __init__(self) -> None:
        """Initialize a new instance of ModuleDescriptor."""
        self.name: Optional[str] = None
        self.host_type: Optional[str] = None
        self.loading_phase: Optional[str] = None
        self.additional_dependencies: List[Any] = []
        self.blacklist_platforms: List[Any] = []
        self.blacklist_programs: List[Any] = []
        self.blacklist_target_configurations: List[Any] = []
        self.blacklist_targets: List[Any] = []
        self.whitelist_platforms: List[Any] = []
        self.whitelist_programs: List[Any] = []
        self.whitelist_target_configurations: List[Any] = []
        self.whitelist_targets: List[Any] = []

    def __repr__(self) -> str:
        """Python interpreter representation of ModuleDescriptor."""
        return f"<ModuleDescriptor {self.name}>"

    def __hash__(self) -> int:
        """Provide a consistent identity."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Provide consistent equality operation."""
        if not isinstance(other, ModuleDescriptor):
            return NotImplemented
        return self.name == other.name

    def __ne__(self, other: object) -> bool:
        """Provide consistent inequality operation."""
        if not isinstance(other, ModuleDescriptor):
            return NotImplemented
        return self.name != other.name

    @staticmethod
    def to_object(dct: Dict[str, Any]) -> Union[ModuleDescriptor, Dict[str, Any]]:
        """Convert a dictionary to an instance of ModuleDescriptor."""
        descriptor = ModuleDescriptor()
        descriptor.name = dct.get("Name")
        descriptor.host_type = dct.get("Type", "Runtime")
        descriptor.loading_phase = dct.get("LoadingPhase", "Default")
        descriptor.blacklist_platforms = dct.get("BlacklistPlatforms", [])
        descriptor.blacklist_programs = dct.get("BlacklistPrograms", [])
        descriptor.blacklist_target_configurations = dct.get(
            "BlacklistTargetConfigurations", []
        )
        descriptor.blacklist_targets = dct.get("BlacklistTargets", [])
        descriptor.whitelist_platforms = dct.get("WhitelistPlatforms", [])
        descriptor.whitelist_programs = dct.get("WhitelistPrograms", [])
        descriptor.whitelist_target_configurations = dct.get(
            "WhitelistTargetConfigurations", []
        )
        descriptor.whitelist_targets = dct.get("WhitelistTargets", [])

        if descriptor.is_valid():
            return descriptor
        return dct

    def to_dict(self) -> Dict[str, Any]:
        """Format this ModuleDescriptor as a dictionary for JSON."""
        return {
            "Name": self.name,
            "Type": self.host_type,
            "LoadingPhase": self.loading_phase,
            "BlacklistPlatforms": self.blacklist_platforms,
            "BlacklistPrograms": self.blacklist_programs,
            "BlacklistTargetConfigurations": self.blacklist_target_configurations,
            "BlacklistTargets": self.blacklist_targets,
            "WhitelistPlatforms": self.whitelist_platforms,
            "WhitelistPrograms": self.whitelist_programs,
            "WhitelistTargetConfigurations": self.whitelist_target_configurations,
            "WhitelistTargets": self.whitelist_targets,
        }

    def is_valid(self) -> bool:
        """Get wehther this ModuleDescriptor is properly constructed."""
        return (
            self.name is not None
            and self.name != ""
            and self.host_type in HOST_TYPES
            and self.loading_phase in LOADING_PHASES
        )
