"""Object wrappers for Unreal projects."""

# Future Standard Library
from __future__ import annotations

# Standard Library
import glob
import json
import os
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional, Union

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
from crazyhusk.engine import UnrealEngine
from crazyhusk.module import ModuleDescriptor
from crazyhusk.plugin import PluginReferenceDescriptor, UnrealPlugin

__all__ = ["UnrealProject"]


class UnrealProjectError(Exception):
    """Custom exception representing errors encountered with UnrealProject."""


class ProjectDescriptor(object):
    """Object wrapper representation of a uproject file, equivalent to serialization method used with FProjectDescriptor.

    https://docs.unrealengine.com/en-US/API/Runtime/Projects/FProjectDescriptor/index.html
    """

    def __init__(self) -> None:
        self.engine_association: Optional[str] = None
        self.category: str = ""
        self.description: str = ""
        self.disable_engine_plugins_by_default: bool = False
        self.is_enterprise_project: bool = False
        self.epic_sample_name_hash: Optional[str] = None
        self.post_build_steps: Optional[List[Any]] = None
        self.pre_build_steps: Optional[List[Any]] = None
        self.target_platforms: List[Any] = []
        self.__plugins: List[Dict[str, Any]] = []
        self.__modules: List[Dict[str, Any]] = []

    def __repr__(self) -> str:
        """Python interpreter representation of ProjectDescriptor."""
        return f"<ProjectDescriptor {self.description}>"

    @property
    def modules(self) -> Iterable[Union[ModuleDescriptor, Dict[str, Any]]]:
        for module in self.__modules:
            yield ModuleDescriptor.to_object(module)

    @property
    def plugins(self) -> Iterable[Union[PluginReferenceDescriptor, Dict[str, Any]]]:
        for plugin in self.__plugins:
            yield PluginReferenceDescriptor.to_object(plugin)

    @staticmethod
    def to_object(dct: Dict[str, Any]) -> Union[ProjectDescriptor, Dict[str, Any]]:
        descriptor = ProjectDescriptor()
        descriptor.engine_association = dct.get("EngineAssociation")
        descriptor.category = dct.get("Category", "")
        descriptor.description = dct.get("Description", "")
        descriptor.disable_engine_plugins_by_default = dct.get(
            "DisableEnginePluginsByDefault", False
        )
        descriptor.is_enterprise_project = dct.get("IsEnterpriseProject", False)
        descriptor.epic_sample_name_hash = dct.get("EpicSampleNameHash")
        descriptor.post_build_steps = dct.get("PostBuildSteps")
        descriptor.pre_build_steps = dct.get("PreBuildSteps")
        descriptor.target_platforms = dct.get("TargetPlatforms", [])
        descriptor.__plugins = dct.get("Plugins", [])
        descriptor.__modules = dct.get("Modules", [])

        if descriptor.is_valid():
            return descriptor
        return dct

    def to_dict(self) -> Dict[str, Any]:
        return {
            "EngineAssociation": self.engine_association,
            "Category": self.category,
            "Description": self.description,
            "DisableEnginePluginsByDefault": self.disable_engine_plugins_by_default,
            "IsEnterpriseProject": self.is_enterprise_project,
            "EpicSampleNameHash": self.epic_sample_name_hash,
            "PostBuildSteps": self.post_build_steps,
            "PreBuildSteps": self.pre_build_steps,
            "TargetPlatforms": self.target_platforms,
            "Modules": list(self.modules),
            "Plugins": list(self.plugins),
        }

    def is_valid(self) -> bool:
        return self.engine_association is not None

    def add_module(self, module: ModuleDescriptor) -> None:
        if not isinstance(module, ModuleDescriptor):
            raise NotImplementedError()
        self.__modules.append(module.to_dict())

    def add_plugin(self, plugin: PluginReferenceDescriptor) -> None:
        if not isinstance(plugin, PluginReferenceDescriptor):
            raise NotImplementedError()
        self.__plugins.append(plugin.to_dict())


class UnrealProject(Buildable):
    """Object wrapper representation of an Unreal Engine project."""

    def __init__(self, project_file: str) -> None:
        """Initialize a new instance of UnrealProject."""
        self.project_file: str = project_file
        self.name: str = os.path.splitext(os.path.basename(project_file))[0]

        self.__descriptor: Optional[ProjectDescriptor] = None
        self.__engine: Optional[UnrealEngine] = None
        self.__modules: Optional[Dict[str, ModuleDescriptor]] = None
        self.__plugins: Optional[Dict[str, UnrealPlugin]] = None
        self.__code_templates: Optional[Dict[str, CodeTemplate]] = None

    def __repr__(self) -> str:
        """Python interpreter representation."""
        return f"<UnrealProject {self.name} at {self.project_file}>"

    @property
    def code_templates(self) -> Dict[str, CodeTemplate]:
        """Get a mapping of this UnrealProject's available C++ code templates."""
        if self.__code_templates is None:
            self.__code_templates = {}
            items = []  # type: List[Union[UnrealProject,UnrealEngine,UnrealPlugin]]
            if self.engine is not None:
                items.append(self.engine)
                if self.engine.plugins is not None and len(self.engine.plugins):
                    items.append(*self.engine.plugins.values())
            items.append(self)
            if self.plugins is not None and len(self.plugins):
                items.append(*self.plugins.values())
            for entry_point in entry_points().get("crazyhusk.code.listers", []):
                for item in items:
                    for template in entry_point.load()(item):
                        self.__code_templates[template.name] = template
        return self.__code_templates

    @property
    def descriptor(self) -> Optional[ProjectDescriptor]:
        """Get an instance of this UnrealProject's associated ProjectDescriptor."""
        if self.__descriptor is None:
            self.validate()

            with open(self.project_file, encoding="utf-8") as json_project_file:
                self.__descriptor = json.load(
                    json_project_file, object_hook=ProjectDescriptor.to_object
                )

        return self.__descriptor

    @property
    def engine(self) -> Optional[UnrealEngine]:
        """Get the associated UnrealEngine object for this Buildable."""
        if self.__engine is None:
            if self.descriptor is not None and self.descriptor.engine_association == "":
                self.__engine = UnrealEngine(
                    os.path.realpath(os.path.join(self.project_file, "..", "..")), ""
                )
            elif (
                self.descriptor is not None
                and self.descriptor.engine_association is not None
            ):
                self.__engine = UnrealEngine.find_engine(
                    self.descriptor.engine_association
                )
        return self.__engine

    @engine.setter
    def engine(self, new_engine: Union[UnrealEngine, str]) -> None:
        """Set the associated UnrealEngine object for this Buildable."""
        if not isinstance(new_engine, UnrealEngine):
            self.__engine = UnrealEngine.find_engine(new_engine)
        else:
            self.__engine = new_engine

    @property
    def project_dir(self) -> str:
        """Get the base directory for .uproject file."""
        return os.path.dirname(self.project_file)

    @property
    def config_dir(self) -> str:
        """Get the project's Config directory."""
        return os.path.join(self.project_dir, "Config")

    @property
    def content_dir(self) -> str:
        """Get the project's Content directory."""
        return os.path.join(self.project_dir, "Content")

    @property
    def plugins_dir(self) -> str:
        """Get the project's Plugins directory."""
        return os.path.join(self.project_dir, "Plugins")

    @property
    def modules(self) -> Optional[Dict[str, ModuleDescriptor]]:
        """Get a mapping of this UnrealProject's associated ModuleDescriptors."""
        if self.__modules is None:
            if self.descriptor is not None:
                self.__modules = {
                    module.name: module
                    for module in self.descriptor.modules
                    if isinstance(module, ModuleDescriptor) and module.name is not None
                }
        return self.__modules

    @property
    def plugins(self) -> Optional[Dict[str, UnrealPlugin]]:
        """Get a mapping of the available plugins installed with this UnrealProject."""
        if self.__plugins is None:
            if self.engine is None:
                self.__plugins = {}
            else:
                self.__plugins = deepcopy(self.engine.plugins)

            for _root, _dirs, _files in os.walk(self.plugins_dir):
                for _file in _files:
                    if os.path.splitext(_file)[-1] == ".uplugin":
                        plugin = UnrealPlugin(os.path.join(_root, _file))
                        if self.__plugins is not None and plugin.name is not None:
                            self.__plugins[plugin.name] = plugin
                        break
        return self.__plugins

    @property
    def saved_dir(self) -> str:
        """Get the project's Saved directory."""
        return os.path.join(self.project_dir, "Saved")

    @property
    def reports_dir(self) -> str:
        """Get the project's default Reports directory."""
        return os.path.join(self.project_dir, "Saved", "Reports")

    # crazyhusk.code.listers
    @staticmethod
    def list_project_code_templates(project: UnrealProject) -> Iterable[CodeTemplate]:
        """Iterate over a given UnrealProject's available C++ code templates."""
        if isinstance(project, UnrealProject):
            for template_filename in glob.iglob(
                os.path.join(project.content_dir, "Editor", "Templates", "*.template")
            ):
                with open(
                    template_filename,
                    encoding="utf-8",
                ) as _template_file:
                    yield CodeTemplate(
                        os.path.basename(os.path.splitext(template_filename)[0]),
                        _template_file.read(),
                    )

    # crazyhusk.project.validators
    @staticmethod
    def project_file_exists(project: UnrealProject) -> None:
        """Raise exception if UnrealProject instance is not available on disk."""
        if not isinstance(project, UnrealProject):
            raise TypeError(
                f"Must provide an instance of crazyhusk.project.UnrealProject, got: {project!r}"
            )
        if not os.path.isfile(project.project_file):
            raise UnrealProjectError(
                f"Specified project file does not exist at {project.project_file}."
            )

    @staticmethod
    def valid_project_file_extension(project: UnrealProject) -> None:
        """Raise exception if UnrealProject instance does not have the correct file extension."""
        if not isinstance(project, UnrealProject):
            raise TypeError(
                f"Must provide an instance of crazyhusk.project.UnrealProject, got: {project!r}"
            )
        if not os.path.splitext(project.project_file)[-1] == ".uproject":
            raise UnrealProjectError(f"Not a uproject file: {project.project_file}")

    def config(
        self, config_category: Optional[str] = None, platform: Optional[str] = None
    ) -> UnrealConfigParser:
        """Create a configuration object associated with this project by category and platform."""
        _config = UnrealConfigParser()
        if isinstance(self.engine, UnrealEngine):
            self.engine.validate()
            _config.read(self.engine.config_files(config_category, platform))
        _config.read(self.config_files(config_category, platform))
        return _config

    def config_files(
        self, config_category: Optional[str] = None, platform: Optional[str] = None
    ) -> Iterable[str]:
        """Iterate configuration file paths associated with this project by category and platform."""
        if config_category in CONFIG_CATEGORIES:
            yield os.path.join(self.config_dir, f"Default{config_category}.ini")
            if platform is not None:
                yield os.path.join(
                    self.config_dir, platform, f"{platform}{config_category}.ini"
                )

    def get_build_command(
        self,
        target: Optional[str] = None,
        configuration: Optional[str] = None,
        platform: Optional[str] = None,
        *extra_switches: str,
        **extra_parameters: str,
    ) -> Iterable[str]:
        """Iterate strings of subprocess arguments to execute the build."""
        if self.engine is None:
            raise UnrealProjectError(
                f"Could not resolve an associated UnrealEngine for project: {self!r}"
            )
        ubt_path = self.engine.executable_path("UnrealBuildTool")
        if ubt_path is None:
            raise UnrealProjectError(
                f"Could not resolve a valid path to UnrealBuildTool for project: {self!r}"
            )
        yield ubt_path
        yield configuration or ""
        yield platform or ""
        switches = {"Progress", "WaitMutex", "NoHotReloadFromIDE"} | set(extra_switches)
        parameters: Dict[str, str] = {
            "Project": self.project_file,
            "TargetType": target or "",
        }
        parameters.update(**extra_parameters)
        for arg in UnrealEngine.format_commandline_options(*switches, **parameters):
            yield arg

    def is_buildable(self) -> bool:
        """Get whether this object is buildable in its current configuration."""
        return self.engine is not None  # TODO: check for .Target.cs files

    def list_tests(
        self, editor: bool = True, *extra_switches: str, **extra_parameters: str
    ) -> int:
        """List available automation tests for this project."""
        switches = {
            "buildmachine",
            "unattended",
            "nopause",
            "nullrhi",
            "stdout",
            "nosplash",
        } | set(extra_switches)

        if editor:
            switches.add("editortest")
        else:
            switches.add("game")

        params = {
            "ExecCmds": "Automation List; quit",
            "TestExit": "Automation Test Queue Empty",
        }
        params.update(extra_parameters)

        if self.engine is not None:
            editor_cmd_path = self.engine.executable_path("UE4Editor-Cmd")
            if editor_cmd_path is not None:
                with self.engine:
                    return self.engine.run(
                        editor_cmd_path,
                        f'"{self.project_file}"',
                        *UnrealEngine.format_commandline_options(*switches, **params),
                    )
        return -1

    def render(
        self,
        map_path: str,
        LevelSequence: str,
        vsync: bool = False,
        *extra_switches: str,
        **extra_parameters: str,
    ) -> int:
        """Run this project in movie scene capture mode."""
        switches = {
            "game",
            "noloadingscreen",
            "unattended",
            "nopause",
            "noscreenmessages",
            "stdout",
            "nosplash",
        } | set(extra_switches)

        if vsync:
            switches.add("VSync")
        else:
            switches.add("NoVSync")

        params = {
            "LevelSequence": LevelSequence,
            "MovieCinematicMode": "yes",
            "MovieSceneCaptureType": "/Script/MovieSceneCapture.AutomatedLevelSequenceCapture",
        }
        params.update(extra_parameters)

        for entry_point in entry_points().get("crazyhusk.render.validators", []):
            entry_point.load()(*switches, **params)

        if self.engine is not None:
            editor_cmd_path = self.engine.executable_path("UE4Editor-Cmd")
            if editor_cmd_path is not None:
                with self.engine:
                    return self.engine.run(
                        editor_cmd_path,
                        f'"{self.project_file}"',
                        map_path,
                        *UnrealEngine.format_commandline_options(*switches, **params),
                    )
        return -1

    def run_tests(
        self,
        tests: List[str],
        report_path: Optional[str] = None,
        editor: bool = True,
        rhi: str = "nullrhi",
        *extra_switches: str,
        **extra_parameters: str,
    ) -> int:
        """Run named automation tests for this project."""
        if report_path is None:
            report_path = self.reports_dir

        switches = {
            rhi,
            "buildmachine",
            "unattended",
            "nopause",
            "stdout",
            "nosplash",
        } | set(extra_switches)

        if editor:
            switches.add("editortest")
        else:
            switches.add("game")

        params = {
            "ExecCmds": "Automation RunTests " + "+".join(tests) + "; quit",
            "TestExit": "Automation Test Queue Empty",
            "ReportOutputPath": report_path,
        }
        params.update(extra_parameters)

        if self.engine is not None:
            editor_cmd_path = self.engine.executable_path("UE4Editor-Cmd")
            if editor_cmd_path is not None:
                with self.engine:
                    return self.engine.run(
                        editor_cmd_path,
                        f'"{self.project_file}"',
                        *UnrealEngine.format_commandline_options(*switches, **params),
                    )
        return -1

    def unreal_path_to_file_path(
        self, unreal_path: str, ext: str = ".uasset"
    ) -> Optional[str]:
        """Convert an Unreal object path to a file path relative to this project."""
        path_split = unreal_path.split("/")
        if len(path_split) < 3:
            raise UnrealProjectError(f"Can't resolve Unreal path: {unreal_path}")

        mount = path_split[1]
        if mount == "Game":
            return os.path.join(self.content_dir, *path_split[2:]) + ext

        if mount == "Engine":
            if not isinstance(self.engine, UnrealEngine):
                raise UnrealProjectError(
                    f"Can't resolve Unreal path: {unreal_path} - could not resolve associated UnrealEngine."
                )
            return os.path.join(self.engine.content_dir, *path_split[2:]) + ext

        if self.plugins is not None and mount in self.plugins:
            return self.plugins[mount].unreal_path_to_file_path(unreal_path, ext)

        raise UnrealProjectError(
            f"Can't resolve Unreal path: {unreal_path} - could not find plugin or feature pack mount {mount}."
        )

    def unreal_path_from_file_path(self, file_path: str) -> Optional[str]:
        """Convert a file path to an appropriate Unreal object path for use with this project."""
        if (
            os.path.commonpath([os.path.realpath(file_path), self.content_dir])
            == self.content_dir
        ):
            sub_path = (
                os.path.splitext(os.path.realpath(file_path))[0]
                .split(self.content_dir)[1][1:]
                .replace(os.sep, "/")
            )
            return f"/Game/{sub_path}"

        if (
            isinstance(self.engine, UnrealEngine)
            and os.path.commonpath(
                [os.path.realpath(file_path), self.engine.content_dir]
            )
            == self.engine.content_dir
        ):
            sub_path = (
                os.path.splitext(os.path.realpath(file_path))[0]
                .split(self.engine.content_dir)[1][1:]
                .replace(os.sep, "/")
            )
            return f"/Engine/{sub_path}"

        if self.plugins is not None:
            for plugin in self.plugins.values():
                unreal_path = plugin.unreal_path_from_file_path(file_path)
                if unreal_path is not None:
                    return unreal_path
        return None

    def validate(self) -> None:
        """Raise exceptions if this instance is misconfigured."""
        for entry_point in entry_points().get("crazyhusk.project.validators", []):
            entry_point.load()(self)
