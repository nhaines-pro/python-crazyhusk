"""Object wrappers for working with Unreal Engine installations."""

# Future Standard Library
from __future__ import annotations

# Standard Library
import glob
import json
import logging
import os
import subprocess
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Set, Tuple, Union

try:
    # Standard Library
    from importlib.metadata import entry_points  # type:ignore
except ImportError:
    # Third Party
    from importlib_metadata import entry_points  # type:ignore

# CrazyHusk
from crazyhusk.build import Buildable
from crazyhusk.code import CodeTemplate
from crazyhusk.config import CONFIG_CATEGORIES, UnrealConfigParser
from crazyhusk.logs import FilterEngineRun

if TYPE_CHECKING:
    # CrazyHusk
    from crazyhusk.plugin import UnrealPlugin

__all__ = ["UnrealEngine", "UnrealEngineError"]


class UnrealEngineError(Exception):
    """Custom exception representing errors encountered with UnrealEngine."""


class UnrealExecutionError(Exception):
    """Custom exception representing errors encountered within a subprocess call of Unreal Engine executables."""


class UnrealVersion(object):
    """Object wrapper representing a Build.version file."""

    def __init__(self) -> None:
        """Initialize a new UnrealVersion."""
        self.major: int = 4
        self.minor: int = 0
        self.patch: int = 0
        self.changelist: int = 0
        self.compatible_changelist: int = 0
        self.is_licensee_version: int = 0
        self.is_promoted_version: int = 1
        self.branch: str = ""

    def __repr__(self) -> str:
        """Python interpreter representation of this instance."""
        return f"<UnrealVersion {self}>"

    def __str__(self) -> str:
        """Represent this instance as a string."""
        result = f"{self.major}.{self.minor}"
        if self.patch:
            result += f".{self.patch}"
        if self.changelist:
            result += f"-{self.changelist}"
        if self.branch != "":
            result += f"+{self.branch}"
        return result

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnrealVersion):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.changelist == other.changelist
            and self.branch == other.branch
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, UnrealVersion):
            return NotImplemented
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
    def to_object(dct: Dict[str, Any]) -> UnrealVersion:
        """Convert mapping form to UnrealVersion object instance."""
        version = UnrealVersion()
        version.major = dct.get("MajorVersion", 4)
        version.minor = dct.get("MinorVersion", 0)
        version.patch = dct.get("PatchVersion", 0)
        version.changelist = dct.get("Changelist", 0)
        version.branch = dct.get("BranchName", "")
        version.compatible_changelist = dct.get("CompatibleChangelist", 0)
        version.is_licensee_version = dct.get("IsLicenseeVersion", 0)
        version.is_promoted_version = dct.get("IsPromotedBuild", 1)
        return version

    def to_dict(self) -> Dict[str, Any]:
        return {
            "MajorVersion": self.major,
            "MinorVersion": self.minor,
            "PatchVersion": self.patch,
            "Changelist": self.changelist,
            "BranchName": self.branch,
            "CompatibleChangelist": self.compatible_changelist,
            "IsLicenseeVersion": self.is_licensee_version,
            "IsPromotedBuild": self.is_promoted_version,
        }


class UnrealEngine(Buildable):
    """Object wrapper representing an Unreal Engine."""

    def __init__(self, base_dir: str, association_name: Optional[str] = None) -> None:
        """Initialize a new UnrealEngine."""
        if base_dir is None:
            raise UnrealEngineError("UnrealEngine base directory must not be None.")
        elif base_dir == "":
            raise UnrealEngineError("UnrealEngine base directory must not be empty.")

        self.base_dir: str = os.path.realpath(base_dir)
        self.association_name: Optional[str] = association_name
        self.__build_targets: Optional[Dict[str, str]] = None
        self.__version: Optional[UnrealVersion] = None
        self.__in_context: bool = False
        self.__plugins: Optional[Dict[str, UnrealPlugin]] = None
        self.__process: Optional[object] = None
        self.__code_templates: Optional[Dict[str, CodeTemplate]] = None

    def __repr__(self) -> str:
        """Python interpreter representation of this instance."""
        return (
            f"<UnrealEngine {self.build_type} Build {self.version} at {self.base_dir}>"
        )

    def __lt__(self, other: object) -> bool:
        """Get whether this UnrealEngine is less than another instance of UnrealEngine."""
        if not isinstance(other, UnrealEngine):
            return NotImplemented
        if self.version is None or other.version is None:
            return NotImplemented
        return self.version < other.version

    def __enter__(self) -> UnrealEngine:
        """Context wrapper entry point.

        Resets the context for running multiple processes sequentially.
        """
        self.__in_context = True
        self.__process = None
        return self

    def __exit__(
        self, exc_type: Optional[Any], exc_val: Optional[Any], exc_tb: Optional[Any]
    ) -> None:
        """Context wrapper exit point.

        Ensures any running subprocesses are terminated.
        """
        if isinstance(self.__process, subprocess.Popen):
            self.__process.kill()
        self.__in_context = False

    @property
    def engine_dir(self) -> str:
        """Path to this Engine's Engine directory."""
        return os.path.join(self.base_dir, "Engine")

    @property
    def feature_packs_dir(self) -> str:
        """Path to this Engine's FeaturePacks directory."""
        return os.path.join(self.base_dir, "FeaturePacks")

    @property
    def samples_dir(self) -> str:
        """Path to this Engine's Samples directory."""
        return os.path.join(self.base_dir, "Samples")

    @property
    def templates_dir(self) -> str:
        """Path to this Engine's Templates directory."""
        return os.path.join(self.base_dir, "Templates")

    @property
    def build_dir(self) -> str:
        """Path to this Engine's Build directory."""
        return os.path.join(self.base_dir, "Engine", "Build")

    @property
    def build_targets(self) -> Dict[str, str]:
        """Get a mapping of this UnrealEngine's available build targets."""
        if self.__build_targets is None:
            self.__build_targets = {}
            for target_file in glob.iglob(
                os.path.join(self.source_dir, "**", "*.Target.cs"), recursive=True
            ):
                target_name = os.path.basename(target_file).split(".")[0]
                self.__build_targets[target_name] = target_file
        return self.__build_targets

    @property
    def build_type(self) -> Optional[str]:
        """Type of build available for this Engine."""
        if os.path.isfile(os.path.join(self.build_dir, "InstalledBuild.txt")):
            return "Installed"
        if os.path.isfile(os.path.join(self.build_dir, "SourceDistribution.txt")):
            return "Source"
        return None

    @property
    def code_templates(self) -> Dict[str, CodeTemplate]:
        """Get a mapping of this UnrealEngine's available C++ code templates."""
        if self.__code_templates is None:
            self.__code_templates = {}
            items = [self]  # type: List[Union[UnrealEngine,UnrealPlugin]]
            if self.plugins is not None:
                for _plugin in self.plugins.values():
                    items.append(_plugin)
            for entry_point in entry_points().get("crazyhusk.code.listers", []):
                for item in items:
                    for template in entry_point.load()(item):
                        self.__code_templates[template.name] = template
        return self.__code_templates

    @property
    def config_dir(self) -> str:
        """Path to this Engine's Config directory."""
        return os.path.join(self.base_dir, "Engine", "Config")

    @property
    def content_dir(self) -> str:
        """Path to this Engine's Content directory."""
        return os.path.join(self.base_dir, "Engine", "Content")

    @property
    def engine(self) -> Optional[UnrealEngine]:
        """Get the associated UnrealEngine object for this Buildable."""
        return self

    @property
    def plugins_dir(self) -> str:
        """Path to this Engine's Plugins directory."""
        return os.path.join(self.base_dir, "Engine", "Plugins")

    @property
    def source_dir(self) -> str:
        """Path to this Engine's Source directory."""
        return os.path.join(self.base_dir, "Engine", "Source")

    @property
    def plugins(self) -> Optional[Dict[str, UnrealPlugin]]:
        """Get a mapping of the available plugins installed with this Engine."""
        # CrazyHusk
        from crazyhusk.plugin import UnrealPlugin

        if self.__plugins is None:
            self.__plugins = {}
            for _root, _dirs, _files in os.walk(self.plugins_dir):
                for _file in _files:
                    if os.path.splitext(_file)[-1] == ".uplugin":
                        plugin = UnrealPlugin(os.path.join(_root, _file))
                        self.__plugins[plugin.name] = plugin
                        break
        return self.__plugins

    @property
    def version(self) -> Optional[UnrealVersion]:
        """Engine version, as UnrealVersion."""
        if self.__version is None and os.path.isfile(
            os.path.join(self.build_dir, "Build.version")
        ):
            with open(
                os.path.join(self.build_dir, "Build.version"), encoding="utf-8"
            ) as json_version_file:
                self.__version = json.load(
                    json_version_file, object_hook=UnrealVersion.to_object
                )
        return self.__version

    @staticmethod
    def find_engine(association: str) -> Optional[UnrealEngine]:
        """Find an engine distribution from EngineAssociation string."""
        for entry_point in entry_points().get("crazyhusk.engine.finders", []):
            engine = entry_point.load()(association)
            if isinstance(engine, UnrealEngine):
                return engine
        return None

    @staticmethod
    def list_all_engines() -> Iterable[UnrealEngine]:
        """List all available engine installations."""
        for entry_point in entry_points().get("crazyhusk.engine.listers", []):
            for engine in entry_point.load()():
                yield engine

    @staticmethod
    def format_commandline_options(*switches: str, **parameters: str) -> Iterable[str]:
        """Convert input arguments from Pythonic expansions to commandline strings."""
        for switch in set(switches):
            yield f"-{switch}"
        for arg, value in parameters.items():
            yield f"-{arg}={value}"

    # crazyhusk.commands
    @staticmethod
    def log_engine_list() -> None:
        """Log all found engines."""
        for engine in sorted(UnrealEngine.list_all_engines()):
            logging.info(engine)

    # crazyhusk.code.listers
    @staticmethod
    def list_engine_code_templates(engine: UnrealEngine) -> Iterable[CodeTemplate]:
        """Iterate over a given UnrealEngine's available C++ code templates."""
        if isinstance(engine, UnrealEngine):
            for template_filename in glob.iglob(
                os.path.join(engine.content_dir, "Editor", "Templates", "*.template")
            ):
                with open(
                    template_filename,
                    encoding="utf-8",
                ) as _template_file:
                    yield CodeTemplate(
                        os.path.basename(os.path.splitext(template_filename)[0]),
                        _template_file.read(),
                    )

    # crazyhusk.engine.sanitizers
    @staticmethod
    def engine_exe_exists(engine: UnrealEngine, executable: str, *args: str) -> None:
        """Raise exception if the executable is not available on disk."""
        if not isinstance(engine, UnrealEngine):
            raise TypeError(
                f"Must provide an instance of crazyhusk.engine.UnrealEngine, got: {engine!r}"
            )
        if not os.path.isfile(os.path.realpath(executable)):
            raise UnrealExecutionError(
                f"Specified executable does not exist: {os.path.realpath(executable)}"
            )

    @staticmethod
    def engine_exe_common_path(
        engine: UnrealEngine, executable: str, *args: str
    ) -> None:
        """Raise exception if the executable does not resolve to a path owned by the given engine."""
        if not isinstance(engine, UnrealEngine):
            raise TypeError(
                f"Must provide an instance of crazyhusk.engine.UnrealEngine, got: {engine!r}"
            )

        if (
            not os.path.commonpath([os.path.realpath(executable), engine.base_dir])
            == engine.base_dir
        ):
            raise UnrealExecutionError(
                f"Specified executable: {os.path.realpath(executable)}\nis not part of the provided engine distribution: {engine!r}"
            )

    # crazyhusk.engine.validators
    @staticmethod
    def engine_dir_exists(engine: UnrealEngine) -> None:
        """Raise exception if this instance is not available on disk."""
        if not isinstance(engine, UnrealEngine):
            raise TypeError(
                f"Must provide an instance of crazyhusk.engine.UnrealEngine, got: {engine!r}"
            )
        if not os.path.isdir(engine.engine_dir):
            raise UnrealEngineError("Specified engine directory does not exist.")

    def config(
        self, config_category: Optional[str] = None, platform: Optional[str] = None
    ) -> UnrealConfigParser:
        """Create a configuration object associated with this engine by category and platform."""
        _config = UnrealConfigParser()
        _config.read(self.config_files(config_category, platform))
        return _config

    def config_files(
        self, config_category: Optional[str] = None, platform: Optional[str] = None
    ) -> Iterable[str]:
        """Iterate configuration file paths associated with this engine by category and platform."""
        yield os.path.join(self.config_dir, "Base.ini")
        if config_category in CONFIG_CATEGORIES:
            yield os.path.join(self.config_dir, f"Base{config_category}.ini")
            if platform is not None:
                yield os.path.join(
                    self.config_dir, platform, f"Base{platform}{config_category}.ini"
                )
                yield os.path.join(
                    self.config_dir, platform, f"{platform}{config_category}.ini"
                )

    def default_build_target(self) -> str:
        """Get the default build target for this Buildable."""
        return "UE4Editor"

    def executable_path(self, executable_name: str) -> Optional[str]:
        """Resolve an expected real path for an executable member of this engine for a given executable name."""
        for entry_point in entry_points().get("crazyhusk.engine.resolvers", []):
            path = entry_point.load()(self, executable_name)
            if path is not None:
                return str(path)
        return None

    def get_build_command(
        self,
        target: Optional[str] = None,
        configuration: Optional[str] = None,
        platform: Optional[str] = None,
        *extra_switches: str,
        **extra_parameters: str,
    ) -> Iterable[str]:
        """Get the default build configuration for this Buildable."""
        ubt_path = self.executable_path("UnrealBuildTool")
        if ubt_path is None:
            raise UnrealEngineError(
                f"Could not resolve a valid path to UnrealBuildTool for engine: {self!r}"
            )
        yield ubt_path
        yield target or ""
        yield configuration or ""
        yield platform or ""

        switches = {"Progress", "WaitMutex"}
        switches.update(*extra_switches)
        for arg in UnrealEngine.format_commandline_options(
            *switches, **extra_parameters
        ):
            yield arg

    def is_buildable(self) -> bool:
        """Get whether this object is buildable in its current configuration."""
        return self.is_source_build()

    def is_installed_build(self) -> bool:
        """Determine if this engine is an Installed distribution."""
        return os.path.isfile(os.path.join(self.build_dir, "InstalledBuild.txt"))

    def is_source_build(self) -> bool:
        """Determine if this engine is a Source distribution."""
        return os.path.isfile(os.path.join(self.build_dir, "SourceDistribution.txt"))

    def is_valid_build_target(self, target: str) -> bool:
        """Get whether a given build target is valid for this Buildable."""
        return target in self.build_targets

    def unreal_path_to_file_path(
        self, unreal_path: str, ext: str = ".uasset"
    ) -> Optional[str]:
        """Convert an Unreal object path to a file path relative to this engine."""
        path_split = unreal_path.split("/")
        if len(path_split) < 3:
            raise UnrealEngineError(f"Can't resolve Unreal path: {unreal_path}")

        mount = path_split[1]
        if mount == "Game":
            raise UnrealEngineError(
                f"Can't resolve Unreal path: {unreal_path} - could not resolve associated UnrealProject."
            )

        if mount == "Engine":
            return os.path.join(self.content_dir, *path_split[2:]) + ext

        if self.plugins is not None and mount in self.plugins:
            return self.plugins[mount].unreal_path_to_file_path(unreal_path, ext)

        raise UnrealEngineError(
            f"Can't resolve Unreal path: {unreal_path} - could not find plugin or feature pack mount {mount}."
        )

    def unreal_path_from_file_path(self, file_path: str) -> str:
        """Convert a file path to an appropriate Unreal object path for use with this engine."""
        if (
            not os.path.commonpath([os.path.realpath(file_path), self.base_dir])
            == self.base_dir
        ):
            raise UnrealEngineError(
                f"File path: {file_path} is not part of this UnrealEngine: {self!r}"
            )

        if (
            os.path.commonpath([os.path.realpath(file_path), self.content_dir])
            == self.content_dir
        ):
            sub_path = (
                os.path.splitext(os.path.realpath(file_path))[0]
                .split(self.content_dir)[1][1:]
                .replace(os.sep, "/")
            )
            return f"/Engine/{sub_path}"

        if self.plugins is not None:
            for plugin in self.plugins.values():
                unreal_path = plugin.unreal_path_from_file_path(file_path)
                if unreal_path is not None:
                    return unreal_path

        raise UnrealEngineError(f"Can't resolve to Unreal path: {file_path}.")

    def validate(self) -> None:
        """Raise exceptions if this instance is misconfigured."""
        for entry_point in entry_points().get("crazyhusk.engine.validators", []):
            entry_point.load()(self)

    def sanitize_commandline(self, executable: str, *args: str) -> List[str]:
        """Raise exceptions if we are about to run unsafe commands in the subprocess."""
        for entry_point in entry_points().get("crazyhusk.engine.sanitizers", []):
            entry_point.load()(self, executable, *args)
        cmd = [executable, *args]
        return cmd

    def run(
        self, executable: str, *args: str, expected_retcodes: Optional[Set[int]] = None
    ) -> int:
        """Run an associated Unreal executable in a subprocess, and process output line by line."""
        if not self.__in_context:
            raise UnrealExecutionError(
                "UnrealEngine.run commands must be called with UnrealEngine as a context wrapper."
            )

        if expected_retcodes is None:
            expected_retcodes = set([0])

        self.validate()
        cmd = self.sanitize_commandline(executable, *args)

        logger = logging.getLogger("UnrealEngine.run")
        logger.addFilter(FilterEngineRun(executable, *args))
        for entry_point in entry_points().get("crazyhusk.engine.filters", []):
            logger.addFilter(entry_point.load()())
        logger.info(" ".join(cmd))

        self.__process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            universal_newlines=True,
        )

        if self.__process.stdout is not None:
            while True:
                output = self.__process.stdout.readline()
                if not output and self.__process.poll() is not None:
                    break
                output = output.strip()
                if not output:
                    continue
                logger.info(output)

        return_code = self.__process.poll()
        if return_code not in expected_retcodes:
            raise UnrealExecutionError(
                f"Unreal executable returned exception with return code {return_code}.\nCommand: {cmd}"
            )
        return return_code
