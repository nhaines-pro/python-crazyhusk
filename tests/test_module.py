# Standard Library
from typing import Any, Type

# Third Party
import pytest

# CrazyHusk
from crazyhusk import module


def test_module_descriptor_init(
    null_module_descriptor: module.ModuleDescriptor,
) -> None:
    assert null_module_descriptor.name is None
    assert null_module_descriptor.host_type is None
    assert null_module_descriptor.loading_phase is None
    assert null_module_descriptor.additional_dependencies == []
    assert null_module_descriptor.blacklist_platforms == []
    assert null_module_descriptor.blacklist_programs == []
    assert null_module_descriptor.blacklist_target_configurations == []
    assert null_module_descriptor.blacklist_targets == []
    assert null_module_descriptor.whitelist_platforms == []
    assert null_module_descriptor.whitelist_programs == []
    assert null_module_descriptor.whitelist_target_configurations == []
    assert null_module_descriptor.whitelist_targets == []


def test_module_descriptor_repr(
    null_module_descriptor: module.ModuleDescriptor,
) -> None:
    assert repr(null_module_descriptor) == "<ModuleDescriptor None>"


def test_module_descriptor_hash(
    null_module_descriptor: module.ModuleDescriptor,
) -> None:
    assert hash(null_module_descriptor) == hash(None)


def test_module_descriptor_equality(
    null_module_descriptor: module.ModuleDescriptor,
    empty_module_descriptor: module.ModuleDescriptor,
) -> None:
    assert null_module_descriptor == null_module_descriptor
    assert null_module_descriptor != empty_module_descriptor


@pytest.mark.parametrize(
    "module_descriptor_fixture,expected",
    [
        ("null_module_descriptor", False),
        ("empty_module_descriptor", False),
        ("invalid_hosttype_module_descriptor", False),
        ("invalid_loadingphase_module_descriptor", False),
        ("default_valid_module_descriptor", True),
    ],
)
def test_module_descriptor_is_valid(
    module_descriptor_fixture: str, expected: bool, request: Any
) -> None:
    module_descriptor = request.getfixturevalue(module_descriptor_fixture)
    assert module_descriptor.is_valid() is expected


@pytest.mark.parametrize(
    "module_descriptor_fixture,expected_type",
    [
        ("null_module_descriptor", dict),
        ("empty_module_descriptor", dict),
        ("invalid_hosttype_module_descriptor", dict),
        ("invalid_loadingphase_module_descriptor", dict),
        ("default_valid_module_descriptor", module.ModuleDescriptor),
    ],
)
def test_module_descriptor_to_object(
    module_descriptor_fixture: str, expected_type: Type[Any], request: Any
) -> None:
    module_descriptor = request.getfixturevalue(module_descriptor_fixture)
    dct = module_descriptor.to_dict()
    assert isinstance(module.ModuleDescriptor.to_object(dct), expected_type)
