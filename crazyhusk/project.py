"""Object wrappers for Unreal projects."""
# Standard Library
import json
import os

# Third Party
import pkg_resources

# CrazyHusk
from crazyhusk.engine import UnrealEngine

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
        self.plugin_reference_descriptors = set()
        self.module_descriptors = set()

    @staticmethod
    def to_object(dct):
        descriptor = ProjectDescriptor()
        descriptor.engine_association = dct.get("EngineAssociation", "")
        descriptor.category = dct.get("Category", "")
        descriptor.description = dct.get("Description", "")
        descriptor.disable_engine_plugins_by_default = dct.get("DisableEnginePluginsByDefault", False)
        descriptor.is_enterprise_project = dct.get("IsEnterpriseProject", False)
        descriptor.epic_sample_name_hash = dct.get("EpicSampleNameHash")
        descriptor.post_build_steps = dct.get("PostBuildSteps")
        descriptor.pre_build_steps = dct.get("PreBuildSteps")
        descriptor.target_platforms = dct.get("TargetPlatforms", [])
        descriptor.plugin_reference_descriptors = set(dct.get("Plugins", []))
        descriptor.module_descriptors = set(dct.get("Modules", []))
        return descriptor


class UnrealProject(object):
    """Object wrapper representation of an Unreal Engine project."""

    def __init__(self, project_file):
        self.project_file = project_file
        self.name = os.path.splitext(os.path.basename(project_file))[0]

        self.__descriptor = None
        self.__engine = None

    def __repr__(self):
        """Python interpreter representation."""
        return f"<UnrealProject {self.name} at {self.project_file}>"

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
    def saved_dir(self):
        """Get the project's Saved directory."""
        return os.path.join(self.project_dir, "Saved")

    # crazyhusk.project.validators
    @staticmethod
    def project_file_exists(project):
        """Raise exception if UnrealProject instance is not available on disk."""
        if not isinstance(project, UnrealProject):
            raise TypeError(
                f"Must provide an instance of crazyhusk.project.UnrealProject, got: {project!r}"
            )
        if not os.path.isfile(project.project_file):
            raise UnrealProjectError("Specified project file does not exist.")

    @staticmethod
    def valid_project_file_extension(project):
        """Raise exception if UnrealProject instance does not have the correct file extension."""
        if not isinstance(project, UnrealProject):
            raise TypeError(
                f"Must provide an instance of crazyhusk.project.UnrealProject, got: {project!r}"
            )
        if not os.path.splitext(project.project_file)[-1] == ".uproject":
            raise UnrealProjectError(f"Not a uproject file: {project.project_file}")

    def validate(self):
        """Raise exceptions if this instance is misconfigured."""
        for entry_point in pkg_resources.iter_entry_points(
            "crazyhusk.project.validators"
        ):
            entry_point.load()(self)
