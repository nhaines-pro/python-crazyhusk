# Third Party
import pytest

# CrazyHusk
from crazyhusk import engine


@pytest.fixture(scope="function")
def version_empty():
    yield engine.UnrealVersion()


@pytest.fixture(scope="function")
def version_5_0():
    version = engine.UnrealVersion()
    version.major = 5
    yield version


@pytest.fixture(scope="function")
def version_26_0():
    version = engine.UnrealVersion()
    version.minor = 26
    return version


@pytest.fixture(scope="function")
def version_26_1():
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 1
    return version


@pytest.fixture(scope="function")
def version_26_1_123456():
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 1
    version.changelist = 123456
    return version


@pytest.fixture(scope="function")
def version_26_1_234567():
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 1
    version.changelist = 234567
    return version


@pytest.fixture(scope="function")
def version_26_1_123456_branch():
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 1
    version.changelist = 123456
    version.branch = "++UE4+Release-4.26"
    return version


@pytest.mark.parametrize(
    "version,major,minor,patch,changelist,branch",
    [
        ("version_empty", 4, 0, 0, 0, ""),
        ("version_26_0", 4, 26, 0, 0, ""),
        ("version_26_1", 4, 26, 1, 0, ""),
        ("version_26_1_123456", 4, 26, 1, 123456, ""),
        ("version_26_1_123456_branch", 4, 26, 1, 123456, "++UE4+Release-4.26"),
    ],
)
def test_unreal_version_init(version, major, minor, patch, changelist, branch, request):
    version = request.getfixturevalue(version)
    assert version.major == major
    assert version.minor == minor
    assert version.patch == patch
    assert version.changelist == changelist
    assert version.branch == branch


@pytest.mark.parametrize(
    "version,version_string",
    [
        ("version_empty", "4.0"),
        ("version_26_0", "4.26"),
        ("version_26_1", "4.26.1"),
        ("version_26_1_123456", "4.26.1-123456"),
        ("version_26_1_123456_branch", "4.26.1-123456+++UE4+Release-4.26"),
    ],
)
def test_unreal_version_string(version, version_string, request):
    version = request.getfixturevalue(version)
    assert str(version) == version_string


@pytest.mark.parametrize(
    "version,version_repr",
    [
        ("version_empty", "<UnrealVersion 4.0>"),
        ("version_26_0", "<UnrealVersion 4.26>"),
        ("version_26_1", "<UnrealVersion 4.26.1>"),
        ("version_26_1_123456", "<UnrealVersion 4.26.1-123456>"),
        (
            "version_26_1_123456_branch",
            "<UnrealVersion 4.26.1-123456+++UE4+Release-4.26>",
        ),
    ],
)
def test_module_descriptor_repr(version, version_repr, request):
    version = request.getfixturevalue(version)
    assert repr(version) == version_repr


@pytest.mark.parametrize(
    "first_version,second_version",
    [
        ("version_empty", "version_26_0"),
        ("version_empty", "version_26_1"),
        ("version_empty", "version_26_1_123456"),
        ("version_empty", "version_26_1_123456_branch"),
        ("version_empty", "version_5_0"),
        ("version_26_0", "version_26_1"),
        ("version_26_0", "version_26_1_123456"),
        ("version_26_0", "version_26_1_123456_branch"),
        ("version_26_0", "version_5_0"),
        ("version_26_1", "version_26_1_123456"),
        ("version_26_1", "version_26_1_123456_branch"),
        ("version_26_1", "version_5_0"),
        ("version_26_1_123456", "version_26_1_234567"),
        ("version_26_1_123456", "version_5_0"),
        ("version_26_1_234567", "version_5_0"),
    ],
)
def test_unreal_version_lt(first_version, second_version, request):
    first_version = request.getfixturevalue(first_version)
    second_version = request.getfixturevalue(second_version)
    assert first_version < second_version

def test_unreal_version_lt_null(version_empty):
    with pytest.raises(TypeError):
        assert version_empty < None

def test_unreal_version_lt_not(version_empty, version_5_0):
    assert not version_5_0 < version_empty

@pytest.mark.parametrize(
    "dct,version_string",
    [
        ({}, "4.0"),
        ({"MajorVersion": 5}, "5.0"),
        ({"MinorVersion": 26}, "4.26"),
        ({"MinorVersion": 26, "PatchVersion": 1}, "4.26.1"),
    ]
)
def test_unreal_version_to_object(dct,version_string):
    assert str(engine.UnrealVersion.to_object(dct)) == version_string



# Tests for UnrealEngine object
