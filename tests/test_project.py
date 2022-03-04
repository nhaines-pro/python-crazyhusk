# Standard Library
import os
import types
from typing import Any, Dict, Optional, Type

# Third Party
import pytest

# CrazyHusk
from crazyhusk import code, config, engine, module, plugin, project


def test_project_descriptor_init(
    null_association_project_descriptor: project.ProjectDescriptor,
) -> None:
    assert null_association_project_descriptor.engine_association is None
    assert null_association_project_descriptor.category == ""
    assert null_association_project_descriptor.description == ""
    assert not null_association_project_descriptor.disable_engine_plugins_by_default
    assert not null_association_project_descriptor.is_enterprise_project
    assert null_association_project_descriptor.epic_sample_name_hash is None
    assert null_association_project_descriptor.post_build_steps is None
    assert null_association_project_descriptor.pre_build_steps is None
    assert isinstance(null_association_project_descriptor.target_platforms, list)
    assert len(null_association_project_descriptor.target_platforms) == 0
    assert isinstance(null_association_project_descriptor.modules, types.GeneratorType)
    assert isinstance(null_association_project_descriptor.plugins, types.GeneratorType)


def test_project_descriptor_repr(
    null_association_project_descriptor: project.ProjectDescriptor,
) -> None:
    assert repr(null_association_project_descriptor) == "<ProjectDescriptor >"


@pytest.mark.parametrize(
    "project_descriptor_fixture,expected_type",
    [
        ("null_association_project_descriptor", dict),
        ("empty_association_project_descriptor", project.ProjectDescriptor),
        ("basic_project_descriptor", project.ProjectDescriptor),
    ],
)
def test_project_descriptor_to_object(
    project_descriptor_fixture: str, expected_type: Type[Any], request: Any
) -> None:
    project_descriptor = request.getfixturevalue(project_descriptor_fixture)
    dct = project_descriptor.to_dict()
    assert isinstance(project.ProjectDescriptor.to_object(dct), expected_type)


def test_project_descriptor_to_object_module_dict(
    basic_project_descriptor_withmodule_dict: Dict[str, Any],
) -> None:
    _project = project.ProjectDescriptor.to_object(
        basic_project_descriptor_withmodule_dict
    )
    assert isinstance(_project, project.ProjectDescriptor)
    for _module in _project.modules:
        assert isinstance(_module, module.ModuleDescriptor)


@pytest.mark.parametrize(
    "project_descriptor_fixture,expected_type",
    [
        ("null_association_project_descriptor", dict),
        ("empty_association_project_descriptor", dict),
        ("basic_project_descriptor", dict),
        ("basic_project_descriptor_withmodule", module.ModuleDescriptor),
    ],
)
def test_project_descriptor_modules(
    project_descriptor_fixture: str, expected_type: Type[Any], request: Any
) -> None:
    project_descriptor = request.getfixturevalue(project_descriptor_fixture)
    for _module in project_descriptor.modules:
        assert isinstance(_module, expected_type)


@pytest.mark.parametrize(
    "project_descriptor_fixture,expected_type",
    [
        ("null_association_project_descriptor", dict),
        ("empty_association_project_descriptor", dict),
        ("basic_project_descriptor", dict),
        (
            "basic_project_descriptor_withpluginreference",
            plugin.PluginReferenceDescriptor,
        ),
    ],
)
def test_project_descriptor_plugins(
    project_descriptor_fixture: str, expected_type: Type[Any], request: Any
) -> None:
    project_descriptor = request.getfixturevalue(project_descriptor_fixture)
    for _plugin in project_descriptor.plugins:
        assert isinstance(_plugin, expected_type)


def test_project_descriptor_add_module(
    basic_project_descriptor: project.ProjectDescriptor,
    default_valid_module_descriptor: module.ModuleDescriptor,
) -> None:
    with pytest.raises(NotImplementedError):
        assert basic_project_descriptor.add_module({}) is None
    assert basic_project_descriptor.add_module(default_valid_module_descriptor) is None


def test_project_descriptor_add_plugin(
    basic_project_descriptor: project.ProjectDescriptor,
    basic_plugin_reference_descriptor: plugin.PluginReferenceDescriptor,
) -> None:
    with pytest.raises(NotImplementedError):
        assert basic_project_descriptor.add_plugin({}) is None
    assert (
        basic_project_descriptor.add_plugin(basic_plugin_reference_descriptor) is None
    )


# UnrealProject tests


@pytest.mark.parametrize(
    "unreal_project_fixture,raises",
    [
        ("null_filename_unreal_project", TypeError),
        ("empty_filename_unreal_project", None),
        ("invalid_filename_unreal_project", None),
        ("empty_file_unreal_project", None),
    ],
)
def test_unreal_project_init_args(
    unreal_project_fixture: str, raises: Optional[Type[BaseException]], request: Any
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert request.getfixturevalue(unreal_project_fixture) is not None
    else:
        assert request.getfixturevalue(unreal_project_fixture) is not None


def test_unreal_project_init(empty_file_unreal_project: project.UnrealProject) -> None:
    assert empty_file_unreal_project.project_file == "MyProject.uproject"
    assert empty_file_unreal_project.name == "MyProject"


def test_unreal_project_repr(empty_file_unreal_project: project.UnrealProject) -> None:
    assert (
        repr(empty_file_unreal_project)
        == "<UnrealProject MyProject at MyProject.uproject>"
    )


def test_unreal_project_properties(
    empty_file_unreal_project: project.UnrealProject,
) -> None:
    assert empty_file_unreal_project.project_dir == ""
    assert empty_file_unreal_project.config_dir == "Config"
    assert empty_file_unreal_project.content_dir == "Content"
    assert empty_file_unreal_project.plugins_dir == "Plugins"
    assert empty_file_unreal_project.saved_dir == "Saved"


@pytest.mark.parametrize(
    "unreal_project_fixture,raises",
    [
        ("empty_filename_unreal_project", project.UnrealProjectError),
        ("invalid_filename_unreal_project", project.UnrealProjectError),
        ("empty_file_content_unreal_project", None),
    ],
)
def test_unreal_project_file_exists(
    unreal_project_fixture: str, raises: Optional[Type[BaseException]], request: Any
) -> None:
    unreal_project = request.getfixturevalue(unreal_project_fixture)
    if raises is not None:
        with pytest.raises(raises):
            assert project.UnrealProject.project_file_exists(unreal_project) is None
    else:
        assert project.UnrealProject.project_file_exists(unreal_project) is None


def test_unreal_project_file_exists_types() -> None:
    with pytest.raises(TypeError):
        assert project.UnrealProject.project_file_exists(None) is None


@pytest.mark.parametrize(
    "unreal_project_fixture,raises",
    [
        ("empty_filename_unreal_project", project.UnrealProjectError),
        ("invalid_filename_unreal_project", project.UnrealProjectError),
        ("empty_file_content_unreal_project", None),
    ],
)
def test_unreal_project_valid_project_file_extension(
    unreal_project_fixture: str, raises: Optional[Type[BaseException]], request: Any
) -> None:
    unreal_project = request.getfixturevalue(unreal_project_fixture)
    if raises is not None:
        with pytest.raises(raises):
            assert (
                project.UnrealProject.valid_project_file_extension(unreal_project)
                is None
            )
    else:
        assert (
            project.UnrealProject.valid_project_file_extension(unreal_project) is None
        )


def test_unreal_project_valid_project_file_extension_types() -> None:
    with pytest.raises(TypeError):
        assert project.UnrealProject.valid_project_file_extension(None) is None


@pytest.mark.parametrize(
    "unreal_project_fixture,expected_type",
    [
        ("basic_unreal_project", module.ModuleDescriptor),
    ],
)
def test_unreal_project_modules(
    unreal_project_fixture: str, expected_type: Type[Any], request: Any
) -> None:
    unreal_project = request.getfixturevalue(unreal_project_fixture)
    for _name, _module in unreal_project.modules.items():
        assert isinstance(_name, str)
        assert isinstance(_module, expected_type)


def test_unreal_project_descriptor(
    basic_unreal_project: project.UnrealProject, monkeypatch: Any
) -> None:
    monkeypatch.setattr(project, "entry_points", lambda: {})
    assert isinstance(basic_unreal_project.descriptor, project.ProjectDescriptor)


@pytest.mark.parametrize(
    "unreal_path,raises,expected",
    [
        ("", project.UnrealProjectError, None),
        ("/", project.UnrealProjectError, None),
        ("/Game", project.UnrealProjectError, None),
        (
            "/Game/whatever",
            None,
            os.path.realpath(os.path.join(".", "Content", "whatever.uasset")),
        ),
        ("/Engine", project.UnrealProjectError, None),
        (
            "/Engine/whatever",
            None,
            os.path.realpath(
                os.path.join("..", "Engine", "Content", "whatever.uasset")
            ),
        ),
        ("/Invalid", project.UnrealProjectError, None),
        ("/Invalid/whatever", project.UnrealProjectError, None),
        ("/test", project.UnrealProjectError, None),
        ("/test/whatever", project.UnrealProjectError, None),
    ],
)
def test_unreal_path_to_file_path(
    unreal_path: str,
    raises: Optional[Type[BaseException]],
    expected: Optional[str],
    basic_unreal_project_realpath: project.UnrealProject,
) -> None:
    if raises:
        with pytest.raises(raises):
            assert (
                basic_unreal_project_realpath.unreal_path_to_file_path(unreal_path)
                == expected
            )
    else:
        assert (
            basic_unreal_project_realpath.unreal_path_to_file_path(unreal_path)
            == expected
        )


@pytest.mark.parametrize(
    "file_path,raises,expected",
    [
        ("", None, None),
        ("/", None, None),
        (".", None, None),
        (os.path.realpath("."), None, None),
        (os.path.realpath("./Content"), None, "/Game/"),
        (
            os.path.realpath(os.path.join(".", "Content", "whatever.uasset")),
            None,
            "/Game/whatever",
        ),
        (os.path.realpath("../Engine/Content"), None, "/Engine/"),
        (
            os.path.realpath(
                os.path.join("..", "Engine", "Content", "whatever.uasset")
            ),
            None,
            "/Engine/whatever",
        ),
    ],
)
def test_unreal_path_from_file_path(
    file_path: str,
    raises: Optional[Type[BaseException]],
    expected: Optional[str],
    basic_unreal_project_realpath: project.UnrealProject,
) -> None:
    if raises:
        with pytest.raises(raises):
            assert (
                basic_unreal_project_realpath.unreal_path_from_file_path(file_path)
                == expected
            )
    else:
        assert (
            basic_unreal_project_realpath.unreal_path_from_file_path(file_path)
            == expected
        )


def test_unreal_project_plugins(
    basic_unreal_project_realpath: project.UnrealProject,
) -> None:
    for _name, _plugin in basic_unreal_project_realpath.plugins.items():
        assert isinstance(_name, str)
        assert isinstance(_plugin, plugin.UnrealPlugin)


def test_unreal_project_code_templates(
    basic_unreal_project_realpath: project.UnrealProject, monkeypatch: Any
) -> None:
    monkeypatch.setattr(project, "entry_points", lambda: {})
    for _name, _plugin in basic_unreal_project_realpath.code_templates.items():
        assert isinstance(_name, str)
        assert isinstance(_plugin, code.CodeTemplate)


@pytest.mark.parametrize(
    "category,platform,expected",
    [
        (None, None, 0),
        ("Engine", None, 1),
        ("Engine", "Windows", 2),
    ],
)
def test_unreal_project_config_files(
    basic_unreal_project_realpath: project.UnrealProject,
    category: Optional[str],
    platform: Optional[str],
    expected: int,
) -> None:
    assert (
        len(list(basic_unreal_project_realpath.config_files(category, platform)))
        == expected
    )


def test_unreal_project_config(
    basic_unreal_project_realpath: project.UnrealProject,
    empty_file_unreal_project: project.UnrealProject,
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(project, "entry_points", lambda: {})
    assert isinstance(basic_unreal_project_realpath.config(), config.UnrealConfigParser)
    assert isinstance(empty_file_unreal_project.config(), config.UnrealConfigParser)


def test_unreal_project_engine(
    basic_unreal_project_realpath: project.UnrealProject,
    null_engine_unreal_project: project.UnrealProject,
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(project, "entry_points", lambda: {})
    assert isinstance(basic_unreal_project_realpath.engine, engine.UnrealEngine)
    assert null_engine_unreal_project.engine is None


def test_unreal_project_list_project_code_templates(
    basic_unreal_project_realpath: project.UnrealProject,
) -> None:
    assert (
        len(
            list(
                project.UnrealProject.list_project_code_templates(
                    basic_unreal_project_realpath
                )
            )
        )
        == 0
    )
