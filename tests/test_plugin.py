# Standard Library
import json
import os
import types

# Third Party
import pytest

# CrazyHusk
from crazyhusk import code, module, plugin


@pytest.fixture(scope="function")
def null_name_plugin_descriptor():
    _plugin = plugin.PluginDescriptor()
    _plugin.friendly_name = None
    yield _plugin


@pytest.fixture(scope="function")
def empty_name_plugin_descriptor():
    yield plugin.PluginDescriptor()


@pytest.fixture(scope="function")
def null_version_plugin_descriptor():
    _plugin = plugin.PluginDescriptor()
    _plugin.friendly_name = "NullVersion"
    _plugin.version_name = None
    yield _plugin


@pytest.fixture(scope="function")
def empty_version_plugin_descriptor():
    _plugin = plugin.PluginDescriptor()
    _plugin.friendly_name = "EmptyVersion"
    yield _plugin


@pytest.fixture(scope="function")
def basic_plugin_descriptor():
    _plugin = plugin.PluginDescriptor()
    _plugin.friendly_name = "Basic"
    _plugin.version_name = "1.0"
    yield _plugin


@pytest.fixture(scope="function")
def default_valid_module_descriptor():
    descriptor = module.ModuleDescriptor()
    descriptor.name = "DefaultValid"
    descriptor.host_type = "Runtime"
    descriptor.loading_phase = "Default"
    yield descriptor


@pytest.fixture(scope="function")
def basic_plugin_descriptor_withmodule(
    basic_plugin_descriptor, default_valid_module_descriptor
):
    basic_plugin_descriptor.add_module(default_valid_module_descriptor)
    yield basic_plugin_descriptor


@pytest.fixture(scope="function")
def basic_plugin_descriptor_withmodule_dict(
    basic_plugin_descriptor, default_valid_module_descriptor
):
    dct = basic_plugin_descriptor.to_dict()
    dct["Modules"].append(default_valid_module_descriptor.to_dict())
    yield dct


def test_plugin_descriptor_init(empty_name_plugin_descriptor):
    assert not empty_name_plugin_descriptor.can_contain_content
    assert not empty_name_plugin_descriptor.explicitly_loaded
    assert not empty_name_plugin_descriptor.installed
    assert not empty_name_plugin_descriptor.is_beta_version
    assert not empty_name_plugin_descriptor.is_experimental_version
    assert not empty_name_plugin_descriptor.is_hidden
    assert not empty_name_plugin_descriptor.is_plugin_extension
    assert not empty_name_plugin_descriptor.requires_build_platform
    assert empty_name_plugin_descriptor.category == ""
    assert empty_name_plugin_descriptor.created_by == ""
    assert empty_name_plugin_descriptor.created_by_url == ""
    assert empty_name_plugin_descriptor.description == ""
    assert empty_name_plugin_descriptor.docs_url == ""
    assert empty_name_plugin_descriptor.editor_custom_virtual_path == ""
    assert not empty_name_plugin_descriptor.enabled_by_default
    assert empty_name_plugin_descriptor.engine_version == ""
    assert empty_name_plugin_descriptor.friendly_name == ""
    assert isinstance(empty_name_plugin_descriptor.localization_targets, list)
    assert len(empty_name_plugin_descriptor.localization_targets) == 0
    assert empty_name_plugin_descriptor.marketplace_url == ""
    assert isinstance(empty_name_plugin_descriptor.modules, types.GeneratorType)
    assert empty_name_plugin_descriptor.parent_plugin_name == ""
    assert isinstance(empty_name_plugin_descriptor.plugins, types.GeneratorType)
    assert empty_name_plugin_descriptor.post_build_steps is None
    assert empty_name_plugin_descriptor.pre_build_steps is None
    assert isinstance(empty_name_plugin_descriptor.supported_programs, list)
    assert len(empty_name_plugin_descriptor.supported_programs) == 0
    assert isinstance(empty_name_plugin_descriptor.supported_target_platforms, list)
    assert len(empty_name_plugin_descriptor.supported_target_platforms) == 0
    assert empty_name_plugin_descriptor.support_url == ""
    assert empty_name_plugin_descriptor.version == 1
    assert empty_name_plugin_descriptor.version_name == ""


def test_plugin_descriptor_repr(empty_name_plugin_descriptor):
    assert repr(empty_name_plugin_descriptor) == "<PluginDescriptor  version >"


@pytest.mark.parametrize(
    "plugin_descriptor,expected_type",
    [
        ("null_name_plugin_descriptor", dict),
        ("empty_name_plugin_descriptor", dict),
        ("null_version_plugin_descriptor", dict),
        ("empty_version_plugin_descriptor", dict),
        ("basic_plugin_descriptor", plugin.PluginDescriptor),
        ("basic_plugin_descriptor_withmodule", plugin.PluginDescriptor),
    ],
)
def test_plugin_descriptor_to_object(plugin_descriptor, expected_type, request):
    plugin_descriptor = request.getfixturevalue(plugin_descriptor)
    dct = plugin_descriptor.to_dict()
    assert isinstance(plugin.PluginDescriptor.to_object(dct), expected_type)


def test_plugin_descriptor_to_object_module_dict(
    basic_plugin_descriptor_withmodule_dict,
):
    _plugin = plugin.PluginDescriptor.to_object(basic_plugin_descriptor_withmodule_dict)
    assert isinstance(_plugin, plugin.PluginDescriptor)
    for _module in _plugin.modules:
        assert isinstance(_module, module.ModuleDescriptor)


@pytest.mark.parametrize(
    "plugin_descriptor,expected_type",
    [
        ("null_name_plugin_descriptor", None),
        ("empty_name_plugin_descriptor", None),
        ("null_version_plugin_descriptor", None),
        ("empty_version_plugin_descriptor", None),
        ("basic_plugin_descriptor", None),
        ("basic_plugin_descriptor_withmodule", module.ModuleDescriptor),
    ],
)
def test_plugin_descriptor_modules(plugin_descriptor, expected_type, request):
    plugin_descriptor = request.getfixturevalue(plugin_descriptor)
    for _module in plugin_descriptor.modules:
        assert isinstance(_module, expected_type)


def test_plugin_descriptor_add_module(
    basic_plugin_descriptor, default_valid_module_descriptor
):
    assert basic_plugin_descriptor.add_module({}) is NotImplemented
    assert basic_plugin_descriptor.add_module(default_valid_module_descriptor) is None


# PluginReferenceDescriptor tests


@pytest.fixture(scope="function")
def null_plugin_reference_descriptor():
    yield plugin.PluginReferenceDescriptor()


@pytest.fixture(scope="function")
def empty_plugin_reference_descriptor():
    ref = plugin.PluginReferenceDescriptor()
    ref.name = ""
    yield ref


@pytest.fixture(scope="function")
def basic_plugin_reference_descriptor():
    ref = plugin.PluginReferenceDescriptor()
    ref.name = "Basic"
    yield ref


def test_plugin_reference_descriptor_init(null_plugin_reference_descriptor):
    assert not null_plugin_reference_descriptor.enabled
    assert isinstance(null_plugin_reference_descriptor.blacklist_platforms, list)
    assert len(null_plugin_reference_descriptor.blacklist_platforms) == 0
    assert isinstance(
        null_plugin_reference_descriptor.blacklist_target_configurations, list
    )
    assert len(null_plugin_reference_descriptor.blacklist_target_configurations) == 0
    assert isinstance(null_plugin_reference_descriptor.blacklist_targets, list)
    assert len(null_plugin_reference_descriptor.blacklist_targets) == 0
    assert not null_plugin_reference_descriptor.optional
    assert null_plugin_reference_descriptor.description == ""
    assert null_plugin_reference_descriptor.marketplace_url == ""
    assert null_plugin_reference_descriptor.name is None
    assert isinstance(null_plugin_reference_descriptor.supported_target_platforms, list)
    assert len(null_plugin_reference_descriptor.supported_target_platforms) == 0
    assert isinstance(null_plugin_reference_descriptor.whitelist_platforms, list)
    assert len(null_plugin_reference_descriptor.whitelist_platforms) == 0
    assert isinstance(
        null_plugin_reference_descriptor.whitelist_target_configurations, list
    )
    assert len(null_plugin_reference_descriptor.whitelist_target_configurations) == 0
    assert isinstance(null_plugin_reference_descriptor.whitelist_targets, list)
    assert len(null_plugin_reference_descriptor.whitelist_targets) == 0


def test_plugin_reference_descriptor_repr(null_plugin_reference_descriptor):
    assert repr(null_plugin_reference_descriptor) == "<PluginReferenceDescriptor None>"


@pytest.mark.parametrize(
    "plugin_descriptor,expected_type",
    [
        ("null_plugin_reference_descriptor", dict),
        ("empty_plugin_reference_descriptor", dict),
        ("basic_plugin_reference_descriptor", plugin.PluginReferenceDescriptor),
    ],
)
def test_plugin_descriptor_to_object(plugin_descriptor, expected_type, request):
    plugin_descriptor = request.getfixturevalue(plugin_descriptor)
    dct = plugin_descriptor.to_dict()
    assert isinstance(plugin.PluginReferenceDescriptor.to_object(dct), expected_type)


# UnrealPlugin tests
@pytest.fixture(scope="function")
def empty_unreal_plugin():
    yield plugin.UnrealPlugin("")


@pytest.fixture(scope="function")
def local_dir_unreal_plugin():
    yield plugin.UnrealPlugin(".")


@pytest.fixture(scope="function")
def invalid_file_unreal_plugin():
    yield plugin.UnrealPlugin("./test.txt")


@pytest.fixture(scope="function")
def invalid_file_unreal_plugin_realpath():
    yield plugin.UnrealPlugin(os.path.realpath("./test.txt"))


@pytest.fixture(scope="function")
def empty_file_content_unreal_plugin(tmp_path):
    plugin_file = tmp_path / "Invalid.uplugin"
    plugin_file.write_text("")
    yield plugin.UnrealPlugin(plugin_file)


@pytest.fixture(scope="function")
def basic_unreal_plugin(tmp_path, basic_plugin_descriptor_withmodule_dict):
    plugin_file = tmp_path / "Basic.uplugin"
    plugin_file.write_text(json.dumps(basic_plugin_descriptor_withmodule_dict))
    yield plugin.UnrealPlugin(plugin_file)


@pytest.mark.parametrize(
    "plugin_file,raises",
    [(None, TypeError), ("", None)],
)
def test_unreal_plugin_init(plugin_file, raises):
    if raises is not None:
        with pytest.raises(raises):
            assert plugin.UnrealPlugin(plugin_file)
    else:
        _plugin = plugin.UnrealPlugin(plugin_file)
        assert _plugin.plugin_file == plugin_file


def test_unreal_plugin_repr(empty_unreal_plugin):
    assert repr(empty_unreal_plugin) == "<UnrealPlugin at >"


@pytest.mark.parametrize(
    "unreal_plugin,plugin_dir,name,config_dir,content_dir",
    [
        ("empty_unreal_plugin", "", "", "Config", "Content"),
        ("local_dir_unreal_plugin", "", ".", "Config", "Content"),
        (
            "invalid_file_unreal_plugin",
            ".",
            "test",
            os.path.join(".", "Config"),
            os.path.join(".", "Content"),
        ),
    ],
)
def test_unreal_plugin_properties(
    unreal_plugin, plugin_dir, name, config_dir, content_dir, request
):
    unreal_plugin = request.getfixturevalue(unreal_plugin)
    assert unreal_plugin.plugin_dir == plugin_dir
    assert unreal_plugin.name == name
    assert unreal_plugin.config_dir == config_dir
    assert unreal_plugin.content_dir == content_dir


@pytest.mark.parametrize(
    "unreal_plugin,raises",
    [
        ("empty_unreal_plugin", plugin.UnrealPluginError),
        ("local_dir_unreal_plugin", plugin.UnrealPluginError),
        ("invalid_file_unreal_plugin", plugin.UnrealPluginError),
        ("empty_file_content_unreal_plugin", None),
    ],
)
def test_unreal_plugin_file_exists(unreal_plugin, raises, request):
    unreal_plugin = request.getfixturevalue(unreal_plugin)
    if raises:
        with pytest.raises(raises):
            assert plugin.UnrealPlugin.plugin_file_exists(unreal_plugin) is None
    else:
        assert plugin.UnrealPlugin.plugin_file_exists(unreal_plugin) is None


def test_unreal_plugin_file_exists_types():
    with pytest.raises(TypeError):
        assert plugin.UnrealPlugin.plugin_file_exists(None)


@pytest.mark.parametrize(
    "unreal_plugin,raises",
    [
        ("empty_unreal_plugin", plugin.UnrealPluginError),
        ("local_dir_unreal_plugin", plugin.UnrealPluginError),
        ("invalid_file_unreal_plugin", plugin.UnrealPluginError),
        ("empty_file_content_unreal_plugin", None),
    ],
)
def test_unreal_plugin_file_extension(unreal_plugin, raises, request):
    unreal_plugin = request.getfixturevalue(unreal_plugin)
    if raises:
        with pytest.raises(raises):
            assert (
                plugin.UnrealPlugin.valid_plugin_file_extension(unreal_plugin) is None
            )
    else:
        assert plugin.UnrealPlugin.valid_plugin_file_extension(unreal_plugin) is None


def test_unreal_plugin_file_extension_types():
    with pytest.raises(TypeError):
        assert plugin.UnrealPlugin.valid_plugin_file_extension(None)


@pytest.mark.parametrize(
    "unreal_path,raises,expected",
    [
        ("", plugin.UnrealPluginError, None),
        ("/", plugin.UnrealPluginError, None),
        ("/Game", plugin.UnrealPluginError, None),
        ("/Game/whatever", plugin.UnrealPluginError, None),
        ("/Engine", plugin.UnrealPluginError, None),
        ("/Engine/whatever", plugin.UnrealPluginError, None),
        ("/Invalid", plugin.UnrealPluginError, None),
        ("/Invalid/whatever", None, None),
        ("/test", plugin.UnrealPluginError, None),
        ("/test/whatever", None, os.path.join(".", "Content", "whatever.uasset")),
    ],
)
def test_unreal_path_to_file_path(
    unreal_path, raises, expected, invalid_file_unreal_plugin
):
    if raises:
        with pytest.raises(raises):
            assert (
                invalid_file_unreal_plugin.unreal_path_to_file_path(unreal_path)
                == expected
            )
    else:
        assert (
            invalid_file_unreal_plugin.unreal_path_to_file_path(unreal_path) == expected
        )


@pytest.mark.parametrize(
    "file_path,raises,expected",
    [
        ("", None, None),
        ("/", None, None),
        (".", None, None),
        (os.path.realpath("."), None, None),
        (os.path.realpath("./Content"), None, "/test/"),
        (
            os.path.realpath(os.path.join(".", "Content", "whatever.uasset")),
            None,
            "/test/whatever",
        ),
    ],
)
def test_unreal_path_from_file_path(
    file_path, raises, expected, invalid_file_unreal_plugin_realpath
):
    if raises:
        with pytest.raises(raises):
            assert (
                invalid_file_unreal_plugin_realpath.unreal_path_from_file_path(
                    file_path
                )
                == expected
            )
    else:
        assert (
            invalid_file_unreal_plugin_realpath.unreal_path_from_file_path(file_path)
            == expected
        )


def test_unreal_plugin_code_templates(empty_file_content_unreal_plugin, monkeypatch):
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: {})
    for _name, _plugin in empty_file_content_unreal_plugin.code_templates.items():
        assert isinstance(_name, str)
        assert isinstance(_plugin, code.CodeTemplate)


def test_unreal_plugin_properties_types(
    empty_file_content_unreal_plugin, basic_unreal_plugin, monkeypatch
):
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: {})
    with pytest.raises(json.decoder.JSONDecodeError):
        assert empty_file_content_unreal_plugin.descriptor is None

    for _name, _module in basic_unreal_plugin.modules.items():
        assert isinstance(_name, str)
        assert isinstance(_module, module.ModuleDescriptor)

    for _name, _ref in basic_unreal_plugin.plugin_refs.items():
        assert isinstance(_name, str)
        assert isinstance(_ref, plugin.PluginReferenceDescriptor)


def test_unreal_plugin_list_plugin_code_templates(basic_unreal_plugin):
    assert (
        len(list(plugin.UnrealPlugin.list_plugin_code_templates(basic_unreal_plugin)))
        == 0
    )


def test(*args):
    return


class test_entry_point:
    def __init__(self) -> None:
        self.name = "test"

    def load(*args):
        return test


class null_entry_point:
    def __init__(self) -> None:
        self.name = "test"

    def load(*args):
        return None


def test_unreal_plugin_validate(basic_unreal_plugin, monkeypatch):
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: {})
    assert basic_unreal_plugin.validate() is None

    monkeypatch.setattr(
        "importlib.metadata.entry_points",
        lambda: {"crazyhusk.plugin.validators": [test_entry_point()]},
    )
    assert basic_unreal_plugin.validate() is None
