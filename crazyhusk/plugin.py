"""Wrapper objects for Unreal plugins."""

# Standard Library
import json
import os

# Third Party
import pkg_resources

__all__ = ["UnrealPlugin"]


class UnrealPluginError(Exception):
    """Custom exception representing errors encountered with Unreal Plugins."""


class PluginDescriptor(object):
    """Object wrapper representation of a uplugin file, equivalent to serialization method used with FPluginDescriptor.

    https://docs.unrealengine.com/en-US/API/Runtime/Projects/FPluginDescriptor/index.html
    """

    def __init__(self):
        """Initialize a PluginDescriptor."""
        self.can_contain_content = False
        self.explicitly_loaded = False
        self.installed = False
        self.is_beta_version = False
        self.is_experimental_version = False
        self.is_hidden = False
        self.is_plugin_extension = False
        self.requires_build_platform = False
        self.category = ""
        self.created_by = ""
        self.created_by_url = ""
        self.description = ""
        self.docs_url = ""
        self.editor_custom_virtual_path = ""
        self.enabled_by_default = False
        self.engine_version = ""
        self.friendly_name = ""
        self.localization_targets = []
        self.marketplace_url = ""
        self.module_descriptors = set()
        self.parent_plugin_name = ""
        self.plugin_descriptors = set()
        self.post_build_steps = None
        self.pre_build_steps = None
        self.supported_programs = []
        self.supported_target_platforms = []
        self.support_url = ""
        self.version = 1
        self.version_name = ""

    def __repr__(self):
        """Python interpreter representation of PluginDescriptor."""
        return f"<PluginDescriptor {self.friendly_name} version {self.version_name}>"

    @staticmethod
    def to_object(dct):
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
        descriptor.module_descriptors = set(dct.get("Modules", []))
        descriptor.parent_plugin_name = dct.get("ParentPluginName", "")
        descriptor.plugin_descriptors = set(dct.get("Plugins", []))
        descriptor.post_build_steps = dct.get("PostBuildSteps")
        descriptor.pre_build_steps = dct.get("PreBuildSteps")
        descriptor.supported_programs = dct.get("SupportedPrograms", [])
        descriptor.supported_target_platforms = dct.get("SupportedTargetPlatforms", [])
        descriptor.support_url = dct.get("SupportURL", "")
        descriptor.version = dct.get("Version", 1)
        descriptor.version_name = dct.get("VersionName", "")
        return descriptor


class UnrealPlugin(object):
    """Object wrapper representation of an Unreal Engine plugin."""

    def __init__(self, plugin_file):
        if plugin_file is None:
            raise TypeError("UnrealPlugin plugin_file must not be None.")

        self.plugin_file = plugin_file
        self.__descriptor = None
        self.__name = None

    def __repr__(self):
        """Python interpreter representation of UnrealPlugin."""
        return f"<UnrealPlugin at {self.plugin_file}>"

    @property
    def descriptor(self):
        if self.__descriptor is None:
            self.validate()

            with open(self.plugin_file, encoding="utf-8") as json_plugin_file:
                self.__descriptor = json.load(
                    json_plugin_file, object_hook=PluginDescriptor.to_object
                )

        return self.__descriptor

    @property
    def name(self):
        if self.__name is None:
            self.__name = os.path.splitext(os.path.basename(self.plugin_file))[0]
        return self.__name

    @property
    def plugin_dir(self):
        """Directory path of this plugin."""
        return os.path.dirname(self.plugin_file)

    @property
    def config_dir(self):
        """Directory path of this plugin's Config."""
        return os.path.join(self.plugin_dir, "Config")

    @property
    def content_dir(self):
        """Directory path of this plugin's Content."""
        return os.path.join(self.plugin_dir, "Content")

    # crazyhusk.plugin.validators
    @staticmethod
    def plugin_file_exists(plugin):
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
    def valid_plugin_file_extension(plugin):
        """Raise exception if UnrealPlugin instance does not have the correct file extension."""
        if not isinstance(plugin, UnrealPlugin):
            raise TypeError(
                f"Must provide an instance of crazyhusk.plugin.UnrealPlugin, got: {plugin!r}"
            )
        if not os.path.splitext(plugin.plugin_file)[-1] == ".uplugin":
            raise UnrealPluginError(f"Not a uplugin file: {plugin.plugin_file}")

    def validate(self):
        """Raise exceptions if this instance is misconfigured."""
        for entry_point in pkg_resources.iter_entry_points(
            "crazyhusk.plugin.validators"
        ):
            entry_point.load()(self)
