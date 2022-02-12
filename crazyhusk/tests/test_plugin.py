# Standard Library
import types

# Third Party
import pytest

# CrazyHusk
from crazyhusk import module, plugin


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
