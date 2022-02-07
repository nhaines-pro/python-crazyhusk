"""Object wrappers for working with Unreal Engine installations."""
# Standard Library
import json
import logging
import os
import subprocess

# Third Party
import pkg_resources

# CrazyHusk
from crazyhusk.config import CONFIG_CATEGORIES, UnrealConfigParser
from crazyhusk.logs import FilterEngineRun

__all__ = ["UnrealEngine", "UnrealEngineError"]


class UnrealEngineError(Exception):
    """Custom exception representing errors encountered with UnrealEngine."""


class UnrealExecutionError(Exception):
    """Custom exception representing errors encountered within a subprocess call of Unreal Engine executables."""


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
        if not (isinstance(self, UnrealVersion) and isinstance(other, UnrealVersion)):
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

        self.base_dir = os.path.realpath(base_dir)
        self.association_name = association_name
        self.__version = None
        self.__in_context = False
        self.__process = None

    def __repr__(self):
        """Python interpreter representation of this instance."""
        return (
            f"<UnrealEngine {self.build_type} Build {self.version} at {self.base_dir}>"
        )

    def __lt__(self, other):
        if not (isinstance(self, UnrealEngine) and isinstance(other, UnrealEngine)):
            return NotImplemented
        return self.version < other.version

    def __enter__(self):
        """Context wrapper entry point.
        Resets the context for running multiple processes sequentially.
        """
        self.__in_context = True
        self.__process = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context wrapper exit point.
        Ensures any running subprocesses are terminated.
        """
        if isinstance(self.__process, subprocess.Popen):
            self.__process.kill()
        self.__in_context = False

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
        """Path to this Engine's Build directory."""
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
    def find_engine(association):
        """Find an engine distribution from EngineAssociation string."""
        for entry_point in pkg_resources.iter_entry_points("crazyhusk.engine.finders"):
            engine = entry_point.load()(association)
            if engine is not None:
                return engine

    @staticmethod
    def list_all_engines():
        """List all available engine installations."""
        for entry_point in pkg_resources.iter_entry_points("crazyhusk.engine.listers"):
            for engine in entry_point.load()():
                yield engine

    @staticmethod
    def format_commandline_options(*switches, **parameters):
        """Convert input arguments from Pythonic expansions to commandline strings."""
        for switch in set(switches):
            yield f"-{switch}"
        for arg, value in parameters.items():
            yield f"-{arg}={value}"

    # crazyhusk.commands
    @staticmethod
    def log_engine_list():
        """Log all found engines."""
        for engine in sorted(UnrealEngine.list_all_engines()):
            logging.info(engine)

    # crazyhusk.engine.sanitizers
    @staticmethod
    def engine_exe_exists(engine, executable, *args):
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
    def engine_exe_common_path(engine, executable, *args):
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
    def engine_dir_exists(engine):
        """Raise exception if this instance is not available on disk."""
        if not isinstance(engine, UnrealEngine):
            raise TypeError(
                f"Must provide an instance of crazyhusk.engine.UnrealEngine, got: {engine!r}"
            )
        if not os.path.isdir(engine.engine_dir):
            raise UnrealEngineError("Specified engine directory does not exist.")

    def config(self, config_category=None, platform=None):
        """Create a configuration object associated with this engine by category and platform."""
        _config = UnrealConfigParser()
        _config.read(self.config_files(config_category, platform))
        return _config

    def config_files(self, config_category=None, platform=None):
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

    def is_installed_build(self):
        """Determine if this engine is an Installed distribution."""
        return os.path.isfile(os.path.join(self.build_dir, "InstalledBuild.txt"))

    def is_source_build(self):
        """Determine if this engine is a Source distribution."""
        return os.path.isfile(os.path.join(self.build_dir, "SourceDistribution.txt"))

    def unreal_path_to_file_path(self, unreal_path, ext=".uasset"):
        """Convert an Unreal object path to a file path relative to this engine."""
        path_split = unreal_path.split("/")
        if len(path_split) < 3:
            raise UnrealEngineError(f"Can't resolve Unreal path: {unreal_path}")

        mount = path_split[1]
        if mount == "Game":
            raise UnrealEngineError(
                f"Can't resolve Unreal path: {unreal_path} - could not resolve associated UnrealProject."
            )
        elif mount == "Engine":
            return f"{os.path.join(self.content_dir, path_split[2:])}{ext}"
        else:
            raise NotImplementedError(
                f"Can't resolve Unreal path: {unreal_path} - could not find plugin or feature pack mount {mount}."
            )

    def unreal_path_from_file_path(self, file_path):
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
        else:
            raise NotImplementedError(
                f"Can't resolve to Unreal path: {file_path} - plugin and feature pack mounts not yet supported."
            )

    def validate(self):
        """Raise exceptions if this instance is misconfigured."""
        for entry_point in pkg_resources.iter_entry_points(
            "crazyhusk.engine.validators"
        ):
            entry_point.load()(self)

    def sanitize_commandline(self, executable, *args):
        """Raise exceptions if we are about to run unsafe commands in the subprocess."""
        for entry_point in pkg_resources.iter_entry_points(
            "crazyhusk.engine.sanitizers"
        ):
            entry_point.load()(self, executable, *args)
        cmd = [executable, *args]
        return cmd

    def run(self, executable, *args, expected_retcodes=None):
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
        for entry_point in pkg_resources.iter_entry_points("crazyhusk.logs.filters"):
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
