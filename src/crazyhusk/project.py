"""Object wrappers for Unreal projects."""

# Standard Library
import glob
import json
import os
from copy import deepcopy

# Third Party
import pkg_resources

# CrazyHusk
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

    def __init__(self):
        self.engine_association = None
        self.category = ""
        self.description = ""
        self.disable_engine_plugins_by_default = False
        self.is_enterprise_project = False
        self.epic_sample_name_hash = None
        self.post_build_steps = None
        self.pre_build_steps = None
        self.target_platforms = []
        self.__plugins = []
        self.__modules = []

    def __repr__(self):
        """Python interpreter representation of ProjectDescriptor."""
        return f"<ProjectDescriptor {self.description}>"

    @property
    def modules(self):
        for module in self.__modules:
            yield ModuleDescriptor.to_object(module)

    @property
    def plugins(self):
        for plugin in self.__plugins:
            yield PluginReferenceDescriptor.to_object(plugin)

    @staticmethod
    def to_object(dct):
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

    def to_dict(self):
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

    def is_valid(self):
        return self.engine_association is not None

    def add_module(self, module):
        if not isinstance(module, ModuleDescriptor):
            return NotImplemented
        self.__modules.append(module)


class UnrealProject(object):
    """Object wrapper representation of an Unreal Engine project."""

    def __init__(self, project_file):
        self.project_file = project_file
        self.name = os.path.splitext(os.path.basename(project_file))[0]

        self.__descriptor = None
        self.__engine = None
        self.__modules = None
        self.__plugins = None
        self.__code_templates = None

    def __repr__(self):
        """Python interpreter representation."""
        return f"<UnrealProject {self.name} at {self.project_file}>"

    @property
    def code_templates(self):
        if self.__code_templates is None:
            self.__code_templates = {}
            if self.engine is None:
                items = (self, *self.plugins.values())
            else:
                items = (
                    self.engine,
                    self.engine.plugins.values(),
                    self,
                    *self.plugins.values(),
                )
            for entry_point in pkg_resources.iter_entry_points(
                "crazyhusk.code.listers"
            ):
                for item in items:
                    for template in entry_point.load()(item):
                        self.__code_templates[template.name] = template
        return self.__code_templates

    @property
    def descriptor(self):
        if self.__descriptor is None:
            self.validate()

            with open(self.project_file, encoding="utf-8") as json_project_file:
                self.__descriptor = json.load(
                    json_project_file, object_hook=ProjectDescriptor.to_object
                )

        return self.__descriptor

    @property
    def engine(self):
        if self.__engine is None:
            if self.descriptor.engine_association == "":
                self.__engine = UnrealEngine(
                    os.path.realpath(os.path.join(self.project_file, "..", "..")), ""
                )
            else:
                self.__engine = UnrealEngine.find_engine(
                    self.descriptor.engine_association
                )
        return self.__engine

    @engine.setter
    def engine(self, new_engine):
        if not isinstance(new_engine, UnrealEngine):
            new_engine = UnrealEngine.find_engine(new_engine)

        new_engine.validate()
        self.__engine = new_engine

    @property
    def project_dir(self):
        """Get the base directory for .uproject file."""
        return os.path.dirname(self.project_file)

    @property
    def config_dir(self):
        """Get the project's Config directory."""
        return os.path.join(self.project_dir, "Config")

    @property
    def content_dir(self):
        """Get the project's Content directory."""
        return os.path.join(self.project_dir, "Content")

    @property
    def plugins_dir(self):
        """Get the project's Plugins directory."""
        return os.path.join(self.project_dir, "Plugins")

    @property
    def modules(self):
        if self.__modules is None:
            self.__modules = {
                module.name: module
                for module in self.descriptor.modules
                if isinstance(module, ModuleDescriptor)
            }
        return self.__modules

    @property
    def plugins(self):
        if self.__plugins is None:
            if self.engine is None:
                self.__plugins = {}
            else:
                self.__plugins = deepcopy(self.engine.plugins)

            for _root, _dirs, _files in os.walk(self.plugins_dir):
                for _file in _files:
                    if os.path.splitext(_file)[-1] == ".uplugin":
                        plugin = UnrealPlugin(os.path.join(_root, _file))
                        self.__plugins[plugin.name] = plugin
                        break
        return self.__plugins

    @property
    def saved_dir(self):
        """Get the project's Saved directory."""
        return os.path.join(self.project_dir, "Saved")

    # crazyhusk.code.listers
    @staticmethod
    def list_project_code_templates(project):
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
    def project_file_exists(project):
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
    def valid_project_file_extension(project):
        """Raise exception if UnrealProject instance does not have the correct file extension."""
        if not isinstance(project, UnrealProject):
            raise TypeError(
                f"Must provide an instance of crazyhusk.project.UnrealProject, got: {project!r}"
            )
        if not os.path.splitext(project.project_file)[-1] == ".uproject":
            raise UnrealProjectError(f"Not a uproject file: {project.project_file}")

    def config(self, config_category=None, platform=None):
        """Create a configuration object associated with this project by category and platform."""
        _config = UnrealConfigParser()
        if isinstance(self.engine, UnrealEngine):
            self.engine.validate()
            _config.read(self.engine.config_files(config_category, platform))
        _config.read(self.config_files(config_category, platform))
        return _config

    def config_files(self, config_category=None, platform=None):
        """Iterate configuration file paths associated with this project by category and platform."""
        if config_category in CONFIG_CATEGORIES:
            yield os.path.join(self.config_dir, f"Default{config_category}.ini")
            if platform is not None:
                yield os.path.join(
                    self.config_dir, platform, f"{platform}{config_category}.ini"
                )

    def unreal_path_to_file_path(self, unreal_path, ext=".uasset"):
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

        if mount in self.plugins:
            return self.plugins[mount].unreal_path_to_file_path(unreal_path, ext)

        raise UnrealProjectError(
            f"Can't resolve Unreal path: {unreal_path} - could not find plugin or feature pack mount {mount}."
        )

    def unreal_path_from_file_path(self, file_path):
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

        for plugin in self.plugins.values():
            unreal_path = plugin.unreal_path_from_file_path(file_path)
            if unreal_path is not None:
                return unreal_path

    def validate(self):
        """Raise exceptions if this instance is misconfigured."""
        for entry_point in pkg_resources.iter_entry_points(
            "crazyhusk.project.validators"
        ):
            entry_point.load()(self)
