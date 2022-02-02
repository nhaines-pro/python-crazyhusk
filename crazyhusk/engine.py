"""Object wrappers for working with Unreal Engine installations."""
import json
import logging
import os

import pkg_resources


__all__ = ["UnrealEngine", "UnrealEngineError"]


class UnrealEngineError(Exception):
    """Custom exception representing errors encountered with UnrealEngine."""


class UnrealVersion(object):
    """Object wrapper representing a Build.version file."""

    def __init__(self):
        """Initialize a new UnrealVersion."""
        self.major = 4
        self.minor = 0
        self.patch = 0
        self.changelist = 0
        self.branch = ""

    def __str__(self):
        """Represent this instance as a string."""
        return f"{self.major}.{self.minor}.{self.patch}-{self.changelist}+{self.branch}"

    def __lt__(self, other):
        if self.major < other.major:
            return True
        if self.minor < other.minor:
            return True
        if self.patch < other.patch:
            return True
        if self.changelist < other.changelist:
            return True
        return False

    @staticmethod
    def to_object(dct):
        """Convert dictionary form to UnrealVersion object instance."""
        version = UnrealVersion()
        version.major = dct.get("MajorVersion", 4)
        version.minor = dct.get("MinorVersion", 0)
        version.patch = dct.get("PatchVersion", 0)
        version.changelist = dct.get("Changelist", 0)
        version.branch = dct.get("BranchName", "")
        return version


class UnrealEngine(object):
    """Object wrapper representing an Unreal Engine."""

    def __init__(self, base_dir, association_name=None):
        """Initialize a new UnrealEngine."""
        if base_dir is None:
            raise UnrealEngineError("UnrealEngine base directory must not be None.")
        elif base_dir == "":
            raise UnrealEngineError("UnrealEngine base directory must not be empty.")

        # dynamically add custom engine finder extensions
        for entry_point in pkg_resources.iter_entry_points("crazyhusk.find_engines"):
            setattr(self, entry_point.name, entry_point.load())

        self.base_dir = base_dir
        self.association_name = association_name
        self.__version = None

    def __repr__(self):
        """Python interpreter representation of this instance."""
        return (
            f"<UnrealEngine {self.build_type} Build {self.version} at {self.base_dir}>"
        )

    def __lt__(self, other):
        return self.version < other.version

    @property
    def engine_dir(self):
        """Path to this Engine's Engine directory."""
        return os.path.join(self.base_dir, "Engine")

    @property
    def feature_packs_dir(self):
        """Path to this Engine's FeaturePacks directory."""
        return os.path.join(self.base_dir, "FeaturePacks")

    @property
    def samples_dir(self):
        """Path to this Engine's Samples directory."""
        return os.path.join(self.base_dir, "Samples")

    @property
    def templates_dir(self):
        """Path to this Engine's Templates directory."""
        return os.path.join(self.base_dir, "Templates")

    @property
    def build_dir(self):
        """Path to this Engine's Binaries directory."""
        return os.path.join(self.base_dir, "Engine", "Build")

    @property
    def build_type(self):
        """Type of build available for this Engine."""
        if os.path.isfile(os.path.join(self.build_dir, "InstalledBuild.txt")):
            return "Installed"
        if os.path.isfile(os.path.join(self.build_dir, "SourceDistribution.txt")):
            return "Source"

    @property
    def config_dir(self):
        """Path to this Engine's Config directory."""
        return os.path.join(self.base_dir, "Engine", "Config")

    @property
    def content_dir(self):
        """Path to this Engine's Content directory."""
        return os.path.join(self.base_dir, "Engine", "Content")

    @property
    def plugins_dir(self):
        """Path to this Engine's Plugins directory."""
        return os.path.join(self.base_dir, "Engine", "Plugins")

    @property
    def version(self):
        """Engine version, as UnrealVersion."""
        if self.__version is None:
            with open(
                os.path.join(self.build_dir, "Build.version"), encoding="utf-8"
            ) as json_version_file:
                self.__version = json.load(
                    json_version_file, object_hook=UnrealVersion.to_object
                )
        return self.__version

    @staticmethod
    def list_engines():
        """Log all found engines."""
        logging.info("Listing all the engines...")
        for engine in sorted(UnrealEngine.find_all_engines()):
            logging.info(engine)

    @staticmethod
    def find_all_engines():
        """Find and yield all available engine installations."""
        for entry_point in pkg_resources.iter_entry_points("crazyhusk.find_engines"):
            for engine in entry_point.load()():
                yield engine

    def is_installed_build(self):
        """Determine if this engine was built via the BuildGraph system. Typically, this means the engine was built by Epic."""
        return os.path.isfile(os.path.join(self.build_dir, "InstalledBuild.txt"))

    def is_source_build(self):
        """Determine if this engine was built as a source distribution. Typically, this means the engine was built locally."""
        return os.path.isfile(os.path.join(self.build_dir, "SourceDistribution.txt"))
