"""Wrapper objects for Unreal plugins."""

# Future Standard Library
from __future__ import annotations

# Standard Library
import glob
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Union

# CrazyHusk
from crazyhusk.build import Buildable
from crazyhusk.engine import UnrealEngine

try:
    # Standard Library
    from importlib.metadata import entry_points  # type:ignore
except ImportError:
    # Third Party
    from importlib_metadata import entry_points  # type:ignore

# CrazyHusk
from crazyhusk.code import CodeTemplate
from crazyhusk.module import ModuleDescriptor

__all__ = ["UnrealPlugin"]


class UnrealPluginError(Exception):
    """Custom exception representing errors encountered with Unreal Plugins."""


class PluginDescriptor(object):
    """Object wrapper representation of a uplugin file, equivalent to serialization method used with FPluginDescriptor.

    https://docs.unrealengine.com/en-US/API/Runtime/Projects/FPluginDescriptor/index.html
    """

    def __init__(self) -> None:
        """Initialize a PluginDescriptor."""
        self.can_contain_content: bool = False
        self.explicitly_loaded: bool = False
        self.installed: bool = False
        self.is_beta_version: bool = False
        self.is_experimental_version: bool = False
        self.is_hidden: bool = False
        self.is_plugin_extension: bool = False
        self.requires_build_platform: bool = False
        self.category: str = ""
        self.created_by: str = ""
        self.created_by_url: str = ""
        self.description: str = ""
        self.docs_url: str = ""
        self.editor_custom_virtual_path: str = ""
        self.enabled_by_default: bool = False
        self.engine_version: str = ""
        self.friendly_name: str = ""
        self.localization_targets: List[Any] = []
        self.marketplace_url: str = ""
        self.__modules: List[Any] = []
        self.parent_plugin_name: str = ""
        self.__plugins: List[Any] = []
        self.post_build_steps: Optional[Any] = None
        self.pre_build_steps: Optional[Any] = None
        self.supported_programs: List[Any] = []
        self.supported_target_platforms: List[Any] = []
        self.support_url: str = ""
        self.version: int = 1
        self.version_name: str = ""

    def __repr__(self) -> str:
        """Python interpreter representation of PluginDescriptor."""
        return f"<PluginDescriptor {self.friendly_name} version {self.version_name}>"

    @property
    def modules(self) -> Iterable[Union[ModuleDescriptor, Dict[str, Any]]]:
        for module in self.__modules:
            if isinstance(module, dict):
                yield ModuleDescriptor.to_object(module)
            else:
                yield module

    @property
    def plugins(self) -> Iterable[Union[PluginReferenceDescriptor, Dict[str, Any]]]:
        for plugin in self.__plugins:
            yield PluginReferenceDescriptor.to_object(plugin)

    @staticmethod
    def to_object(dct: Dict[str, Any]) -> Union[PluginDescriptor, Dict[str, Any]]:
        descriptor = PluginDescriptor()
        descriptor.can_contain_content = dct.get("CanContainContent", False)
        descriptor.explicitly_loaded = dct.get("ExplicitlyLoaded", False)
        descriptor.installed = dct.get("Installed", False)
        descriptor.is_beta_version = dct.get("IsBetaVersion", False)
        descriptor.is_experimental_version = dct.get("IsExperimentalVersion", False)
        descriptor.is_hidden = dct.get("IsHidden", False)
        descriptor.is_plugin_extension = dct.get("IsPluginExtension", False)
        descriptor.requires_build_platform = dct.get("RequiresBuildPlatform", False)
        descriptor.category = dct.get("Category", "")
        descriptor.created_by = dct.get("CreatedBy", "")
        descriptor.created_by_url = dct.get("CreatedByURL", "")
        descriptor.description = dct.get("Description", "")
        descriptor.docs_url = dct.get("DocsURL", "")
        descriptor.editor_custom_virtual_path = dct.get("EditorCustomVirtualPath", "")
        descriptor.enabled_by_default = dct.get("EnabledByDefault", False)
        descriptor.engine_version = dct.get("EngineVersion", "")
        descriptor.friendly_name = dct.get("FriendlyName", "")
        descriptor.localization_targets = dct.get("LocalizationTargets", [])
        descriptor.marketplace_url = dct.get("MarketplaceURL", "")
        descriptor.__modules = dct.get("Modules", [])
        descriptor.parent_plugin_name = dct.get("ParentPluginName", "")
        descriptor.__plugins = dct.get("Plugins", [])
        descriptor.post_build_steps = dct.get("PostBuildSteps")
        descriptor.pre_build_steps = dct.get("PreBuildSteps")
        descriptor.supported_programs = dct.get("SupportedPrograms", [])
        descriptor.supported_target_platforms = dct.get("SupportedTargetPlatforms", [])
        descriptor.support_url = dct.get("SupportURL", "")
        descriptor.version = dct.get("Version", 1)
        descriptor.version_name = dct.get("VersionName", "")

        if descriptor.is_valid():
            return descriptor
        return dct

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CanContainContent": self.can_contain_content,
            "ExplicitlyLoaded": self.explicitly_loaded,
            "Installed": self.installed,
            "IsBetaVersion": self.is_beta_version,
            "IsExperimentalVersion": self.is_experimental_version,
            "IsHidden": self.is_hidden,
            "IsPluginExtension": self.is_plugin_extension,
            "RequiresBuildPlatform": self.requires_build_platform,
            "Category": self.category,
            "CreatedBy": self.created_by,
            "CreatedByURL": self.created_by_url,
            "Description": self.description,
            "DocsURL": self.docs_url,
            "EditorCustomVirtualPath": self.editor_custom_virtual_path,
            "EnabledByDefault": self.enabled_by_default,
            "EngineVersion": self.engine_version,
            "FriendlyName": self.friendly_name,
            "LocalizationTargets": self.localization_targets,
            "MarketplaceURL": self.marketplace_url,
            "Modules": list(self.modules),
            "ParentPluginName": self.parent_plugin_name,
            "Plugins": list(self.plugins),
            "PostBuildSteps": self.post_build_steps,
            "PreBuildSteps": self.pre_build_steps,
            "SupportedPrograms": self.supported_programs,
            "SupportedTargetPlatforms": self.supported_target_platforms,
            "SupportURL": self.support_url,
            "Version": self.version,
            "VersionName": self.version_name,
        }

    def is_valid(self) -> bool:
        return (
            self.friendly_name is not None
            and self.friendly_name != ""
            and self.version_name is not None
            and self.version_name != ""
        )

    def add_module(self, module: ModuleDescriptor) -> None:
        if not isinstance(module, ModuleDescriptor):
            raise NotImplementedError()
        self.__modules.append(module)


class PluginReferenceDescriptor(object):
    """Object wrapper representation of Unreal Plugin descriptor reference, equivalent to FPluginReferenceDescriptor.

    https://docs.unrealengine.com/en-US/API/Runtime/Projects/FPluginReferenceDescriptor/index.html
    """

    def __init__(self) -> None:
        """Initialize a new instance of PluginReferenceDescriptor."""
        self.enabled: bool = False
        self.blacklist_platforms: List[Any] = []
        self.blacklist_target_configurations: List[Any] = []
        self.blacklist_targets: List[Any] = []
        self.optional: bool = False
        self.description: str = ""
        self.marketplace_url: str = ""
        self.name: Optional[str] = None
        self.supported_target_platforms: List[Any] = []
        self.whitelist_platforms: List[Any] = []
        self.whitelist_target_configurations: List[Any] = []
        self.whitelist_targets: List[Any] = []

    def __repr__(self) -> str:
        """Python interpreter representation of PluginReferenceDescriptor."""
        return f"<PluginReferenceDescriptor {self.name}>"

    @staticmethod
    def to_object(
        dct: Dict[str, Any]
    ) -> Union[PluginReferenceDescriptor, Dict[str, Any]]:
        ref = PluginReferenceDescriptor()
        ref.enabled = dct.get("Enabled", False)
        ref.blacklist_platforms = dct.get("BlacklistPlatforms", [])
        ref.blacklist_target_configurations = dct.get(
            "BlacklistTargetConfigurations", []
        )
        ref.blacklist_targets = dct.get("BlacklistTargets", [])
        ref.optional = dct.get("Optional", False)
        ref.description = dct.get("Description", "")
        ref.marketplace_url = dct.get("MarketplaceURL", "")
        ref.name = dct.get("Name")
        ref.supported_target_platforms = dct.get("SupportedTargetPlatforms", [])
        ref.whitelist_platforms = dct.get("WhitelistPlatforms", [])
        ref.whitelist_target_configurations = dct.get(
            "WhitelistTargetConfigurations", []
        )
        ref.whitelist_targets = dct.get("WhitelistTargets", [])

        if ref.is_valid():
            return ref
        return dct

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Enabled": self.enabled,
            "BlacklistPlatforms": self.blacklist_platforms,
            "BlacklistTargetConfigurations": self.blacklist_target_configurations,
            "BlacklistTargets": self.blacklist_targets,
            "Optional": self.optional,
            "Description": self.description,
            "MarketplaceURL": self.marketplace_url,
            "Name": self.name,
            "SupportedTargetPlatforms": self.supported_target_platforms,
            "WhitelistPlatforms": self.whitelist_platforms,
            "WhitelistTargetConfigurations": self.whitelist_target_configurations,
            "WhitelistTargets": self.whitelist_targets,
        }

    def is_valid(self) -> bool:
        return self.name is not None and self.name != ""


class UnrealPlugin(Buildable):
    """Object wrapper representation of an Unreal Engine plugin."""

    def __init__(self, plugin_file: str) -> None:
        """Initialize a new instance of UnrealPlugin."""
        if plugin_file is None:
            raise TypeError("UnrealPlugin plugin_file must not be None.")

        self.plugin_file: str = plugin_file
        self.__descriptor: Optional[PluginDescriptor] = None
        self.__name: Optional[str] = None
        self.__modules: Optional[Dict[str, ModuleDescriptor]] = None
        self.__plugin_refs: Optional[Dict[str, PluginReferenceDescriptor]] = None
        self.__code_templates: Optional[Dict[str, CodeTemplate]] = None

    def __repr__(self) -> str:
        """Python interpreter representation of UnrealPlugin."""
        return f"<UnrealPlugin at {self.plugin_file}>"

    @property
    def code_templates(self) -> Dict[str, CodeTemplate]:
        """Get a mapping of this UnrealPlugin's available C++ code templates."""
        if self.__code_templates is None:
            self.__code_templates = {
                template.name: template
                for entry_point in entry_points().get("crazyhusk.code.listers", [])
                for template in entry_point.load()(self)
            }
        return self.__code_templates

    @property
    def descriptor(self) -> PluginDescriptor:
        """Get an instance of this UnrealPlugin's associated PluginDescriptor."""
        if self.__descriptor is None:
            self.validate()

            with open(self.plugin_file, encoding="utf-8") as json_plugin_file:
                self.__descriptor = json.load(
                    json_plugin_file, object_hook=PluginDescriptor.to_object
                )

        return self.__descriptor

    @property
    def engine(self) -> Optional[UnrealEngine]:
        """Get the associated UnrealEngine object for this Buildable."""
        return None

    @property
    def modules(self) -> Dict[str, ModuleDescriptor]:
        """Get a mapping of this UnrealPlugin's associated ModuleDescriptors."""
        if self.__modules is None:
            self.__modules = {
                module.name: module
                for module in self.descriptor.modules
                if isinstance(module, ModuleDescriptor) and module.name is not None
            }
        return self.__modules

    @property
    def name(self) -> str:
        """Get the name of this UnrealPlugin."""
        if self.__name is None:
            self.__name = os.path.splitext(os.path.basename(self.plugin_file))[0]
        return self.__name

    @property
    def plugin_dir(self) -> str:
        """Directory path of this plugin."""
        return os.path.dirname(self.plugin_file)

    @property
    def plugin_refs(self) -> Dict[str, PluginReferenceDescriptor]:
        """Get a mapping of PluginReferenceDescriptors for this UnrealPlugin."""
        if self.__plugin_refs is None:
            self.__plugin_refs = {
                plugin.name: plugin
                for plugin in self.descriptor.plugins
                if isinstance(plugin, PluginReferenceDescriptor)
                and plugin.name is not None
            }
        return self.__plugin_refs

    @property
    def config_dir(self) -> str:
        """Directory path of this plugin's Config."""
        return os.path.join(self.plugin_dir, "Config")

    @property
    def content_dir(self) -> str:
        """Directory path of this plugin's Content."""
        return os.path.join(self.plugin_dir, "Content")

    # crazyhusk.code.listers
    @staticmethod
    def list_plugin_code_templates(plugin: UnrealPlugin) -> Iterable[CodeTemplate]:
        """Iterate over a given UnrealPlugin's available C++ code templates."""
        if isinstance(plugin, UnrealPlugin):
            for template_filename in glob.iglob(
                os.path.join(plugin.content_dir, "Editor", "Templates", "*.template")
            ):
                with open(
                    template_filename,
                    encoding="utf-8",
                ) as _template_file:
                    yield CodeTemplate(
                        os.path.basename(os.path.splitext(template_filename)[0]),
                        _template_file.read(),
                    )

    # crazyhusk.plugin.validators
    @staticmethod
    def plugin_file_exists(plugin: UnrealPlugin) -> None:
        """Raise exception if UnrealPlugin instance is not available on disk."""
        if not isinstance(plugin, UnrealPlugin):
            raise TypeError(
                f"Must provide an instance of crazyhusk.plugin.UnrealPlugin, got: {plugin!r}"
            )
        if not os.path.isfile(plugin.plugin_file):
            raise UnrealPluginError(
                f"Specified plugin descriptor file does not exist at {plugin.plugin_file}."
            )

    @staticmethod
    def valid_plugin_file_extension(plugin: UnrealPlugin) -> None:
        """Raise exception if UnrealPlugin instance does not have the correct file extension."""
        if not isinstance(plugin, UnrealPlugin):
            raise TypeError(
                f"Must provide an instance of crazyhusk.plugin.UnrealPlugin, got: {plugin!r}"
            )
        if not os.path.splitext(plugin.plugin_file)[-1] == ".uplugin":
            raise UnrealPluginError(f"Not a uplugin file: {plugin.plugin_file}")

    def get_build_command(
        self,
        target: Optional[str] = None,
        configuration: Optional[str] = None,
        platform: Optional[str] = None,
        *extra_switches: str,
        **extra_parameters: str,
    ) -> Iterable[str]:
        """Iterate strings of subprocess arguments to execute the build."""
        raise StopIteration

    def is_buildable(self) -> bool:
        """Get whether this object is buildable in its current configuration."""
        return False

    def unreal_path_to_file_path(
        self, unreal_path: str, ext: str = ".uasset"
    ) -> Optional[str]:
        """Convert an Unreal object path to a file path relative to this plugin."""
        path_split = unreal_path.split("/")
        if len(path_split) < 3:
            raise UnrealPluginError(f"Can't resolve Unreal path: {unreal_path}")

        mount = path_split[1]
        if mount == "Game":
            raise UnrealPluginError(
                f"Can't resolve Unreal path: {unreal_path} - could not resolve associated UnrealProject."
            )
        if mount == "Engine":
            raise UnrealPluginError(
                f"Can't resolve Unreal path: {unreal_path} - could not resolve associated UnrealEngine."
            )
        if mount == self.name:
            return os.path.join(self.content_dir, *path_split[2:]) + ext
        return None

    def unreal_path_from_file_path(self, file_path: str) -> Optional[str]:
        """Convert a file path to an appropriate Unreal object path for use with this plugin."""
        if (
            os.path.commonpath([os.path.realpath(file_path), self.content_dir])
            == self.content_dir
        ):
            sub_path = (
                os.path.splitext(os.path.realpath(file_path))[0]
                .split(self.content_dir)[1][1:]
                .replace(os.sep, "/")
            )
            return f"/{self.name}/{sub_path}"
        return None

    def validate(self) -> None:
        """Raise exceptions if this instance is misconfigured."""
        for entry_point in entry_points().get("crazyhusk.plugin.validators", []):
            entry_point.load()(self)
