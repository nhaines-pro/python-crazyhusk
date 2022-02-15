# Standard Library
import types

# Third Party
import pytest

# CrazyHusk
from crazyhusk import module, project


@pytest.fixture(scope="function")
def null_association_project_descriptor():
    yield project.ProjectDescriptor()


@pytest.fixture(scope="function")
def empty_association_project_descriptor():
    _project = project.ProjectDescriptor()
    _project.engine_association = ""
    yield _project


@pytest.fixture(scope="function")
def basic_project_descriptor():
    _project = project.ProjectDescriptor()
    _project.description = "Basic"
    _project.engine_association = "4.26"
    yield _project


@pytest.fixture(scope="function")
def default_valid_module_descriptor():
    descriptor = module.ModuleDescriptor()
    descriptor.name = "DefaultValid"
    descriptor.host_type = "Runtime"
    descriptor.loading_phase = "Default"
    yield descriptor


@pytest.fixture(scope="function")
def basic_project_descriptor_withmodule(
    basic_project_descriptor, default_valid_module_descriptor
):
    basic_project_descriptor.add_module(default_valid_module_descriptor)
    yield basic_project_descriptor


@pytest.fixture(scope="function")
def basic_project_descriptor_withmodule_dict(
    basic_project_descriptor, default_valid_module_descriptor
):
    dct = basic_project_descriptor.to_dict()
    dct["Modules"].append(default_valid_module_descriptor.to_dict())
    yield dct


def test_project_descriptor_init(null_association_project_descriptor):
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


def test_project_descriptor_repr(null_association_project_descriptor):
    assert repr(null_association_project_descriptor) == "<ProjectDescriptor >"


@pytest.mark.parametrize(
    "project_descriptor,expected_type",
    [
        ("null_association_project_descriptor", dict),
        ("empty_association_project_descriptor", project.ProjectDescriptor),
        ("basic_project_descriptor", project.ProjectDescriptor),
    ],
)
def test_project_descriptor_to_object(project_descriptor, expected_type, request):
    project_descriptor = request.getfixturevalue(project_descriptor)
    dct = project_descriptor.to_dict()
    assert isinstance(project.ProjectDescriptor.to_object(dct), expected_type)


def test_project_descriptor_to_object_module_dict(
    basic_project_descriptor_withmodule_dict,
):
    _project = project.ProjectDescriptor.to_object(
        basic_project_descriptor_withmodule_dict
    )
    assert isinstance(_project, project.ProjectDescriptor)
    for _module in _project.modules:
        assert isinstance(_module, module.ModuleDescriptor)


@pytest.mark.parametrize(
    "project_descriptor,expected_type",
    [
        ("null_association_project_descriptor", dict),
        ("empty_association_project_descriptor", project.ProjectDescriptor),
        ("basic_project_descriptor", project.ProjectDescriptor),
    ],
)
def test_project_descriptor_modules(project_descriptor, expected_type, request):
    project_descriptor = request.getfixturevalue(project_descriptor)
    for _module in project_descriptor.modules:
        assert isinstance(_module, expected_type)


def test_project_descriptor_add_module(
    basic_project_descriptor, default_valid_module_descriptor
):
    assert basic_project_descriptor.add_module({}) is NotImplemented
    assert basic_project_descriptor.add_module(default_valid_module_descriptor) is None


# UnrealProject tests


@pytest.fixture(scope="function")
def null_filename_unreal_project():
    yield project.UnrealProject(None)


@pytest.fixture(scope="function")
def empty_filename_unreal_project():
    yield project.UnrealProject("")


@pytest.fixture(scope="function")
def invalid_filename_unreal_project():
    yield project.UnrealProject("MyProject.txt")


@pytest.fixture(scope="function")
def empty_file_unreal_project():
    yield project.UnrealProject("MyProject.uproject")


@pytest.fixture(scope="function")
def empty_file_content_unreal_project(tmp_path):
    project_file = tmp_path / "MyProject.uproject"
    project_file.write_text("")
    yield project.UnrealProject(project_file)


@pytest.mark.parametrize(
    "unreal_project,raises",
    [
        ("null_filename_unreal_project", TypeError),
        ("empty_filename_unreal_project", None),
        ("invalid_filename_unreal_project", None),
        ("empty_file_unreal_project", None),
    ],
)
def test_unreal_project_init_args(unreal_project, raises, request):
    if raises is not None:
        with pytest.raises(raises):
            assert request.getfixturevalue(unreal_project)
    else:
        assert request.getfixturevalue(unreal_project)


def test_unreal_project_init(empty_file_unreal_project):
    assert empty_file_unreal_project.project_file == "MyProject.uproject"
    assert empty_file_unreal_project.name == "MyProject"


def test_unreal_project_repr(empty_file_unreal_project):
    assert (
        repr(empty_file_unreal_project)
        == "<UnrealProject MyProject at MyProject.uproject>"
    )


def test_unreal_project_properties(empty_file_unreal_project):
    assert empty_file_unreal_project.project_dir == ""
    assert empty_file_unreal_project.config_dir == "Config"
    assert empty_file_unreal_project.content_dir == "Content"
    assert empty_file_unreal_project.plugins_dir == "Plugins"
    assert empty_file_unreal_project.saved_dir == "Saved"


@pytest.mark.parametrize(
    "unreal_project,raises",
    [
        ("empty_filename_unreal_project", project.UnrealProjectError),
        ("invalid_filename_unreal_project", project.UnrealProjectError),
        ("empty_file_content_unreal_project", None),
    ],
)
def test_unreal_project_file_exists(unreal_project, raises, request):
    unreal_project = request.getfixturevalue(unreal_project)
    if raises is not None:
        with pytest.raises(raises):
            assert project.UnrealProject.project_file_exists(unreal_project) is None
    else:
        assert project.UnrealProject.project_file_exists(unreal_project) is None


def test_unreal_project_file_exists_types():
    with pytest.raises(TypeError):
        assert project.UnrealProject.project_file_exists(None) is None


@pytest.mark.parametrize(
    "unreal_project,raises",
    [
        ("empty_filename_unreal_project", project.UnrealProjectError),
        ("invalid_filename_unreal_project", project.UnrealProjectError),
        ("empty_file_content_unreal_project", None),
    ],
)
def test_unreal_project_valid_project_file_extension(unreal_project, raises, request):
    unreal_project = request.getfixturevalue(unreal_project)
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


def test_unreal_project_valid_project_file_extension_types():
    with pytest.raises(TypeError):
        assert project.UnrealProject.valid_project_file_extension(None) is None
