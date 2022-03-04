"""Monkeypatching for module-level issues, such as mocking winreg"""

# Future Standard Library
from __future__ import annotations

# Standard Library
import json
import os
import sys
from types import ModuleType, TracebackType
from typing import Any, Callable, Dict, Iterable, Optional, Type
from xml.etree.ElementTree import Element

# Third Party
import pytest

# CrazyHusk
from crazyhusk import code, config, engine, logs, module, plugin, project


@pytest.fixture(scope="function")
def mock_winreg(monkeypatch: Any) -> None:
    class HKEYType:
        def __bool__(self) -> bool:
            ...

        def __int__(self) -> int:
            ...

        def __enter__(self) -> HKEYType:
            ...

        def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[Type[BaseException]],
            exc_tb: Optional[Type[TracebackType]],
        ) -> bool | None:
            ...

        def Close(self) -> None:
            ...

        def Detach(self) -> int:
            ...

    def OpenKey(key: Any, sub_key: str, reserved: int = 0, access: int = 0) -> HKEYType:
        return HKEYType()

    def OpenKeyEx(
        key: Any, sub_key: str, reserved: int = 0, access: int = 0
    ) -> HKEYType:
        return HKEYType()

    def EnumValue(key: HKEYType, index: int) -> tuple[str, Any, int]:
        raise OSError()

    def QueryValueEx(__key: HKEYType, __name: str) -> tuple[Any, int]:
        raise OSError()

    module = ModuleType("winreg")
    setattr(module, "OpenKey", OpenKey)
    setattr(module, "OpenKeyEx", OpenKeyEx)
    setattr(module, "EnumValue", EnumValue)
    setattr(module, "QueryValueEx", QueryValueEx)
    setattr(module, "HKEY_CURRENT_USER", 1)
    setattr(module, "HKEY_LOCAL_MACHINE", 1)
    monkeypatch.setitem(sys.modules, "winreg", module)


@pytest.fixture(scope="function")
def null_code_template() -> code.CodeTemplate:
    yield code.CodeTemplate(None)


@pytest.fixture(scope="function")
def empty_code_template() -> code.CodeTemplate:
    yield code.CodeTemplate("")


@pytest.fixture(scope="function")
def basic_code_template() -> code.CodeTemplate:
    yield code.CodeTemplate("Basic", "%TEST_TOKEN%")


@pytest.fixture(scope="function")
def multiline_basic_code_template() -> code.CodeTemplate:
    yield code.CodeTemplate("MultilineBasic", "//%TEST_TOKEN%\n//%TEST_TOKEN%")


@pytest.fixture(scope="function")
def multiline_multitoken_code_template() -> code.CodeTemplate:
    yield code.CodeTemplate(
        "MultilineMultitoken", r"//%TEST_TOKEN_1%\n//%TEST_TOKEN_2%"
    )


@pytest.fixture(scope="function")
def empty_parser() -> config.UnrealConfigParser:
    yield config.UnrealConfigParser()


@pytest.fixture(scope="function")
def version_empty() -> engine.UnrealVersion:
    yield engine.UnrealVersion()


@pytest.fixture(scope="function")
def version_5_0() -> engine.UnrealVersion:
    version = engine.UnrealVersion()
    version.major = 5
    yield version


@pytest.fixture(scope="function")
def version_26_0() -> engine.UnrealVersion:
    version = engine.UnrealVersion()
    version.minor = 26
    return version


@pytest.fixture(scope="function")
def version_26_1() -> engine.UnrealVersion:
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 1
    return version


@pytest.fixture(scope="function")
def version_26_1_123456() -> engine.UnrealVersion:
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 1
    version.changelist = 123456
    return version


@pytest.fixture(scope="function")
def version_26_1_234567() -> engine.UnrealVersion:
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 1
    version.changelist = 234567
    return version


@pytest.fixture(scope="function")
def version_26_1_123456_branch() -> engine.UnrealVersion:
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 1
    version.changelist = 123456
    version.branch = "++UE4+Release-4.26"
    return version


@pytest.fixture(scope="function")
def version_egl_4_26_2() -> engine.UnrealVersion:
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 2
    version.changelist = 15973114
    version.branch = "++UE4+Release-4.26"
    return version


@pytest.fixture(scope="function")
def engine_empty(tmp_path: Any) -> engine.UnrealEngine:
    yield engine.UnrealEngine(tmp_path / "Empty")


@pytest.fixture(scope="function")
def engine_local() -> engine.UnrealEngine:
    yield engine.UnrealEngine(".")


@pytest.fixture(scope="function")
def engine_empty_version_empty(
    tmp_path: Any, version_empty: engine.UnrealVersion
) -> engine.UnrealEngine:
    tmp_engine_dir = tmp_path / "EmptyVersion"
    tmp_engine_dir.mkdir()
    engine_dir = tmp_engine_dir / "Engine"
    engine_dir.mkdir()
    build_dir = engine_dir / "Build"
    build_dir.mkdir()
    version_file = build_dir / "Build.version"
    version_file.write_text(json.dumps(version_empty.to_dict()))
    source_file = build_dir / "SourceDistribution.txt"
    source_file.write_text("")
    yield engine.UnrealEngine(tmp_engine_dir)


@pytest.fixture(scope="function")
def engine_empty_version_egl_4_26_2(
    tmp_path: Any, version_egl_4_26_2: engine.UnrealVersion
) -> engine.UnrealEngine:
    tmp_engine_dir = tmp_path / "EGL4.26.2"
    tmp_engine_dir.mkdir()
    engine_dir = tmp_engine_dir / "Engine"
    engine_dir.mkdir()
    build_dir = engine_dir / "Build"
    build_dir.mkdir()
    version_file = build_dir / "Build.version"
    version_file.write_text(json.dumps(version_egl_4_26_2.to_dict()))
    installed_file = build_dir / "InstalledBuild.txt"
    installed_file.write_text("")
    config_dir = engine_dir / "Config"
    config_dir.mkdir()
    base_config_file = config_dir / "Base.ini"
    base_config_file.write_text("")
    yield engine.UnrealEngine(tmp_engine_dir)


@pytest.fixture(scope="function")
def null_filter_engine_run() -> logs.FilterEngineRun:
    yield logs.FilterEngineRun(None)


@pytest.fixture(scope="function")
def empty_filter_engine_run() -> logs.FilterEngineRun:
    yield logs.FilterEngineRun("")


@pytest.fixture(scope="function")
def one_arg_filter_engine_run() -> logs.FilterEngineRun:
    yield logs.FilterEngineRun("", "arg")


@pytest.fixture(scope="function")
def multi_arg_filter_engine_run() -> logs.FilterEngineRun:
    yield logs.FilterEngineRun("", "arg1", "arg2", "arg3")


@pytest.fixture(scope="function")
def null_module_descriptor() -> module.ModuleDescriptor:
    yield module.ModuleDescriptor()


@pytest.fixture(scope="function")
def empty_module_descriptor() -> module.ModuleDescriptor:
    descriptor = module.ModuleDescriptor()
    descriptor.name = ""
    yield descriptor


@pytest.fixture(scope="function")
def invalid_hosttype_module_descriptor() -> module.ModuleDescriptor:
    descriptor = module.ModuleDescriptor()
    descriptor.name = "InvalidHostType"
    descriptor.host_type = "Invalid"
    yield descriptor


@pytest.fixture(scope="function")
def invalid_loadingphase_module_descriptor() -> module.ModuleDescriptor:
    descriptor = module.ModuleDescriptor()
    descriptor.name = "InvalidLoadingPhase"
    descriptor.host_type = "Runtime"
    descriptor.loading_phase = "Invalid"
    yield descriptor


@pytest.fixture(scope="function")
def default_valid_module_descriptor() -> module.ModuleDescriptor:
    descriptor = module.ModuleDescriptor()
    descriptor.name = "DefaultValid"
    descriptor.host_type = "Runtime"
    descriptor.loading_phase = "Default"
    yield descriptor


@pytest.fixture(scope="function")
def null_name_plugin_descriptor() -> plugin.PluginDescriptor:
    _plugin = plugin.PluginDescriptor()
    _plugin.friendly_name = None
    yield _plugin


@pytest.fixture(scope="function")
def empty_name_plugin_descriptor() -> plugin.PluginDescriptor:
    yield plugin.PluginDescriptor()


@pytest.fixture(scope="function")
def null_version_plugin_descriptor() -> plugin.PluginDescriptor:
    _plugin = plugin.PluginDescriptor()
    _plugin.friendly_name = "NullVersion"
    _plugin.version_name = None
    yield _plugin


@pytest.fixture(scope="function")
def empty_version_plugin_descriptor() -> plugin.PluginDescriptor:
    _plugin = plugin.PluginDescriptor()
    _plugin.friendly_name = "EmptyVersion"
    yield _plugin


@pytest.fixture(scope="function")
def basic_plugin_descriptor() -> plugin.PluginDescriptor:
    _plugin = plugin.PluginDescriptor()
    _plugin.friendly_name = "Basic"
    _plugin.version_name = "1.0"
    yield _plugin


@pytest.fixture(scope="function")
def basic_plugin_descriptor_withmodule(
    basic_plugin_descriptor: plugin.PluginDescriptor,
    default_valid_module_descriptor: module.ModuleDescriptor,
) -> plugin.PluginDescriptor:
    basic_plugin_descriptor.add_module(default_valid_module_descriptor)
    yield basic_plugin_descriptor


@pytest.fixture(scope="function")
def basic_plugin_descriptor_withmodule_dict(
    basic_plugin_descriptor: plugin.PluginDescriptor,
    default_valid_module_descriptor: module.ModuleDescriptor,
) -> Iterable[Dict[str, Any]]:
    dct = basic_plugin_descriptor.to_dict()
    dct["Modules"].append(default_valid_module_descriptor.to_dict())
    yield dct


@pytest.fixture(scope="function")
def null_plugin_reference_descriptor() -> plugin.PluginReferenceDescriptor:
    yield plugin.PluginReferenceDescriptor()


@pytest.fixture(scope="function")
def empty_plugin_reference_descriptor() -> plugin.PluginReferenceDescriptor:
    ref = plugin.PluginReferenceDescriptor()
    ref.name = ""
    yield ref


@pytest.fixture(scope="function")
def basic_plugin_reference_descriptor() -> plugin.PluginReferenceDescriptor:
    ref = plugin.PluginReferenceDescriptor()
    ref.name = "Basic"
    yield ref


@pytest.fixture(scope="function")
def empty_unreal_plugin() -> plugin.UnrealPlugin:
    yield plugin.UnrealPlugin("")


@pytest.fixture(scope="function")
def local_dir_unreal_plugin() -> plugin.UnrealPlugin:
    yield plugin.UnrealPlugin(".")


@pytest.fixture(scope="function")
def invalid_file_unreal_plugin() -> plugin.UnrealPlugin:
    yield plugin.UnrealPlugin("./test.txt")


@pytest.fixture(scope="function")
def invalid_file_unreal_plugin_realpath() -> plugin.UnrealPlugin:
    yield plugin.UnrealPlugin(os.path.realpath("./test.txt"))


@pytest.fixture(scope="function")
def empty_file_content_unreal_plugin(tmp_path: Any) -> plugin.UnrealPlugin:
    plugin_file = tmp_path / "Invalid.uplugin"
    plugin_file.write_text("")
    yield plugin.UnrealPlugin(plugin_file)


@pytest.fixture(scope="function")
def basic_unreal_plugin(
    tmp_path: Any, basic_plugin_descriptor_withmodule_dict: Iterable[Dict[str, Any]]
) -> plugin.UnrealPlugin:
    plugin_file = tmp_path / "Basic.uplugin"
    plugin_file.write_text(json.dumps(basic_plugin_descriptor_withmodule_dict))
    yield plugin.UnrealPlugin(plugin_file)


@pytest.fixture(scope="function")
def null_association_project_descriptor() -> project.ProjectDescriptor:
    yield project.ProjectDescriptor()


@pytest.fixture(scope="function")
def empty_association_project_descriptor() -> project.ProjectDescriptor:
    _project = project.ProjectDescriptor()
    _project.engine_association = ""
    yield _project


@pytest.fixture(scope="function")
def basic_project_descriptor() -> project.ProjectDescriptor:
    _project = project.ProjectDescriptor()
    _project.description = "Basic"
    _project.engine_association = ""
    yield _project


@pytest.fixture(scope="function")
def basic_project_descriptor_withmodule(
    basic_project_descriptor: project.ProjectDescriptor,
    default_valid_module_descriptor: module.ModuleDescriptor,
) -> project.ProjectDescriptor:
    basic_project_descriptor.add_module(default_valid_module_descriptor)
    yield basic_project_descriptor


@pytest.fixture(scope="function")
def basic_project_descriptor_withpluginreference(
    basic_project_descriptor: project.ProjectDescriptor,
    basic_plugin_reference_descriptor: plugin.PluginReferenceDescriptor,
) -> project.ProjectDescriptor:
    basic_project_descriptor.add_plugin(basic_plugin_reference_descriptor)
    yield basic_project_descriptor


@pytest.fixture(scope="function")
def basic_project_descriptor_withmodule_dict(
    basic_project_descriptor: project.ProjectDescriptor,
    default_valid_module_descriptor: module.ModuleDescriptor,
) -> Iterable[Dict[str, Any]]:
    dct = basic_project_descriptor.to_dict()
    dct["Modules"].append(default_valid_module_descriptor.to_dict())
    yield dct


@pytest.fixture(scope="function")
def null_filename_unreal_project() -> project.UnrealProject:
    yield project.UnrealProject(None)


@pytest.fixture(scope="function")
def empty_filename_unreal_project() -> project.UnrealProject:
    yield project.UnrealProject("")


@pytest.fixture(scope="function")
def invalid_filename_unreal_project() -> project.UnrealProject:
    yield project.UnrealProject("MyProject.txt")


@pytest.fixture(scope="function")
def empty_file_unreal_project() -> project.UnrealProject:
    yield project.UnrealProject("MyProject.uproject")


@pytest.fixture(scope="function")
def empty_file_content_unreal_project(tmp_path: Any) -> project.UnrealProject:
    project_file = tmp_path / "MyProject.uproject"
    project_file.write_text("")
    yield project.UnrealProject(project_file)


@pytest.fixture(scope="function")
def null_engine_unreal_project(tmp_path: Any) -> project.UnrealProject:
    project.entry_points = lambda: {}
    project_file = tmp_path / "MyProject.uproject"
    project_file.write_text('{"EngineAssociation":"123456"}')
    _project = project.UnrealProject(project_file)
    _project.engine = None
    yield _project


@pytest.fixture(scope="function")
def basic_unreal_project(
    tmp_path: Any, basic_project_descriptor_withmodule_dict: Iterable[Dict[str, Any]]
) -> project.UnrealProject:
    project_file = tmp_path / "MyProject.uproject"
    project_file.write_text(json.dumps(basic_project_descriptor_withmodule_dict))
    yield project.UnrealProject(project_file)


@pytest.fixture(scope="function")
def basic_unreal_project_realpath(
    basic_project_descriptor_withmodule_dict: Iterable[Dict[str, Any]]
) -> project.UnrealProject:
    project_file = os.path.realpath("./MyProject.uproject")
    engine_dir = os.path.realpath("../Engine")
    os.makedirs(engine_dir, exist_ok=True)
    with open(project_file, "w", encoding="utf-8") as _file:
        json.dump(basic_project_descriptor_withmodule_dict, _file)
    yield project.UnrealProject(project_file)
    os.remove(project_file)
    os.removedirs(engine_dir)


@pytest.fixture(scope="function")
def null_report_file() -> None:
    return None


@pytest.fixture(scope="function")
def empty_filename_report_file() -> str:
    return ""


@pytest.fixture(scope="function")
def non_json_report_file(tmp_path: Any) -> str:
    non_json_file = tmp_path / "non-json.file"
    non_json_file.write_text("")
    return str(non_json_file)


@pytest.fixture(scope="function")
def empty_json_report_file(tmp_path: Any) -> str:
    empty_json_file = tmp_path / "empty.json"
    empty_json_file.write_text("")
    return str(empty_json_file)


@pytest.fixture(scope="function")
def list_json_report_file(tmp_path: Any) -> str:
    list_json_file = tmp_path / "list.json"
    list_json_file.write_text("[]")
    return str(list_json_file)


@pytest.fixture(scope="function")
def empty_dict_json_report_file(tmp_path: Any) -> str:
    empty_dict_json_file = tmp_path / "empty_dict.json"
    empty_dict_json_file.write_text("{}")
    return str(empty_dict_json_file)


@pytest.fixture(scope="function")
def xml_filename_report_file(tmp_path: Any) -> str:
    return str(tmp_path / "empty.xml")


@pytest.fixture(scope="function")
def xml_filename_mkdirs_report_file(tmp_path: Any) -> str:
    return str(tmp_path / "test/empty.xml")


@pytest.fixture(scope="function")
def null_test_suites() -> None:
    return None


@pytest.fixture(scope="function")
def emptystring_test_suites() -> str:
    return ""


@pytest.fixture(scope="function")
def empty_element_test_suites() -> Element:
    return Element("")


@pytest.fixture(scope="function")
def basic_element_test_suites() -> Element:
    return Element("testsuites")


@pytest.fixture(scope="function")
def null_entry_point() -> object:
    class NullEntryPoint:
        def __init__(self) -> None:
            self.name = "test"

        def load(*args: Any) -> None:
            return None

    yield NullEntryPoint()


@pytest.fixture(scope="function")
def test_entry_point() -> object:
    def test(*args: Any) -> None:
        return

    class TestEntryPoint:
        def __init__(self) -> None:
            self.name = "test"

        def load(*args: Any) -> Callable[[], None]:
            return test

    yield TestEntryPoint()


@pytest.fixture(scope="function")
def basic_datfile(tmp_path: Any) -> Iterable[str]:
    yield json.dumps(
        {
            "InstallationList": [
                {
                    "InstallLocation": "C:\\EpicStore\\UE_4.26",
                    "NamespaceId": "ue",
                    "ItemId": "3ddb1bad6e004b99a7192c1a29f2318a",
                    "ArtifactId": "UE_4.26",
                    "AppVersion": "4.26.2-15973114+++UE4+Release-4.26-Windows",
                    "AppName": "UE_4.26",
                },
            ]
        }
    )
