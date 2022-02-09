"""Wrapper objects for Unreal code modules."""

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

    def __init__(self):
        """Initialize a new instance of ModuleDescriptor."""
        self.name = None
        self.host_type = None
        self.loading_phase = None
        self.additional_dependencies = []
        self.blacklist_platforms = []
        self.blacklist_programs = []
        self.blacklist_target_configurations = []
        self.blacklist_targets = []
        self.whitelist_platforms = []
        self.whitelist_programs = []
        self.whitelist_target_configurations = []
        self.whitelist_targets = []

    def __hash__(self):
        """Provide a consistent identity."""
        return hash(self.name)

    def __eq__(self, other):
        """Provide consistent equality operation."""
        return self.name == other.name

    def __ne__(self, other):
        """Provide consistent inequality operation."""
        return self.name != other.name

    @staticmethod
    def to_object(dct):
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

    def is_valid(self):
        return (
            self.name is not None
            and self.friendly_name != ""
            and self.host_type in HOST_TYPES
            and self.loading_phase in LOADING_PHASES
        )
