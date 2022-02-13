# Standard Library
import json
import os

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


@pytest.fixture(scope="function")
def version_egl_4_26_2():
    version = engine.UnrealVersion()
    version.minor = 26
    version.patch = 2
    version.changelist = 15973114
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
    "first_version,second_version",
    [
        ("version_empty", "version_empty"),
        ("version_26_0", "version_26_0"),
        ("version_26_1", "version_26_1"),
        ("version_26_1_123456", "version_26_1_123456"),
        ("version_26_1_234567", "version_26_1_234567"),
        ("version_5_0", "version_5_0"),
    ],
)
def test_unreal_version_eq(first_version, second_version, request):
    first_version = request.getfixturevalue(first_version)
    second_version = request.getfixturevalue(second_version)
    assert first_version == second_version


def test_unreal_version_eq_null(version_empty):
    assert not version_empty == None


@pytest.mark.parametrize(
    "dct,version_string",
    [
        ({}, "4.0"),
        ({"MajorVersion": 5}, "5.0"),
        ({"MinorVersion": 26}, "4.26"),
        ({"MinorVersion": 26, "PatchVersion": 1}, "4.26.1"),
    ],
)
def test_unreal_version_to_object(dct, version_string):
    assert str(engine.UnrealVersion.to_object(dct)) == version_string


# Tests for UnrealEngine object
@pytest.mark.parametrize(
    "base_dir,raises,expected",
    [
        (None, engine.UnrealEngineError, None),
        ("", engine.UnrealEngineError, None),
        (".", None, os.path.realpath(".")),
    ],
)
def test_unreal_engine_init(base_dir, raises, expected):
    if raises is not None:
        with pytest.raises(raises):
            assert engine.UnrealEngine(base_dir)
    else:
        assert engine.UnrealEngine(base_dir).base_dir == expected


@pytest.fixture(scope="function")
def engine_empty(tmp_path):
    yield engine.UnrealEngine(tmp_path / "Empty")

@pytest.fixture(scope="function")
def engine_local():
    yield engine.UnrealEngine(".")

@pytest.fixture(scope="function")
def engine_empty_version_empty(tmp_path, version_empty):
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
def engine_empty_version_egl_4_26_2(tmp_path, version_egl_4_26_2):
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
    yield engine.UnrealEngine(tmp_engine_dir)


def test_unreal_engine_repr(engine_empty):
    assert (
        repr(engine_empty)
        == f"<UnrealEngine None Build None at {engine_empty.base_dir}>"
    )


def test_unreal_engine_lt_types(engine_empty, engine_empty_version_empty):
    with pytest.raises(TypeError):
        assert engine_empty < None
        assert engine_empty < engine_empty_version_empty


def test_unreal_engine_lt(engine_empty_version_empty, engine_empty_version_egl_4_26_2):
    assert engine_empty_version_empty < engine_empty_version_egl_4_26_2


def test_unreal_engine_dir_properties(engine_empty_version_egl_4_26_2):
    assert engine_empty_version_egl_4_26_2.engine_dir == os.path.join(
        engine_empty_version_egl_4_26_2.base_dir, "Engine"
    )
    assert engine_empty_version_egl_4_26_2.feature_packs_dir == os.path.join(
        engine_empty_version_egl_4_26_2.base_dir, "FeaturePacks"
    )
    assert engine_empty_version_egl_4_26_2.samples_dir == os.path.join(
        engine_empty_version_egl_4_26_2.base_dir, "Samples"
    )
    assert engine_empty_version_egl_4_26_2.templates_dir == os.path.join(
        engine_empty_version_egl_4_26_2.base_dir, "Templates"
    )
    assert engine_empty_version_egl_4_26_2.build_dir == os.path.join(
        engine_empty_version_egl_4_26_2.base_dir, "Engine", "Build"
    )
    assert engine_empty_version_egl_4_26_2.config_dir == os.path.join(
        engine_empty_version_egl_4_26_2.base_dir, "Engine", "Config"
    )
    assert engine_empty_version_egl_4_26_2.content_dir == os.path.join(
        engine_empty_version_egl_4_26_2.base_dir, "Engine", "Content"
    )
    assert engine_empty_version_egl_4_26_2.plugins_dir == os.path.join(
        engine_empty_version_egl_4_26_2.base_dir, "Engine", "Plugins"
    )

@pytest.mark.parametrize(
    "unreal_engine,expected",
    [
        ("engine_empty", None),
        ("engine_empty_version_egl_4_26_2", "Installed"),
        ("engine_empty_version_empty", "Source")
    ],
)
def test_unreal_engine_build_type(unreal_engine,expected,request):
    unreal_engine = request.getfixturevalue(unreal_engine)
    assert unreal_engine.build_type == expected


@pytest.mark.parametrize(
    "unreal_engine,executable,raises",
    [
        ("engine_local", None, TypeError),
        ("engine_local", ".", None),
        ("engine_local", "/bin/scary_dir/important_exe", engine.UnrealExecutionError),
        ("engine_local", os.path.realpath(".."), engine.UnrealExecutionError),
    ],
)
def test_unreal_engine_exe_common_path(unreal_engine,executable,raises,request):
    unreal_engine = request.getfixturevalue(unreal_engine)
    if raises is not None:
        with pytest.raises(raises):
            assert engine.UnrealEngine.engine_exe_common_path(unreal_engine, executable)
    else:
        assert engine.UnrealEngine.engine_exe_common_path(unreal_engine, executable) is None

def test_unreal_engine_exe_common_path_types():
    with pytest.raises(TypeError):
        assert engine.UnrealEngine.engine_exe_common_path(None, None)


@pytest.mark.parametrize(
    "unreal_engine,executable,raises",
    [
        ("engine_empty", "", engine.UnrealExecutionError),
        ("engine_empty_version_egl_4_26_2", "", engine.UnrealExecutionError),
        ("engine_empty_version_empty", "", engine.UnrealExecutionError),
        ("engine_local", None, TypeError),
        ("engine_local", ".", engine.UnrealExecutionError),
        ("engine_local", "/bin/scary_dir/important_exe", engine.UnrealExecutionError),
        ("engine_local", r"C:\Windows\scaryfile.exe", engine.UnrealExecutionError),
        ("engine_local", os.path.realpath(".."), engine.UnrealExecutionError),
    ],
)
def test_unreal_engine_exe_exists(unreal_engine,executable,raises,request):
    unreal_engine = request.getfixturevalue(unreal_engine)
    if raises is not None:
        with pytest.raises(raises):
            assert engine.UnrealEngine.engine_exe_exists(unreal_engine, executable)
    else:
        assert engine.UnrealEngine.engine_exe_exists(unreal_engine, executable) is None


def test_unreal_engine_exe_exists_types():
    with pytest.raises(TypeError):
        assert engine.UnrealEngine.engine_exe_exists(None, None)


@pytest.mark.parametrize(
    "unreal_engine,raises",
    [
        ("engine_empty", engine.UnrealEngineError),
        ("engine_empty_version_egl_4_26_2", None),
        ("engine_empty_version_empty", None),
        ("engine_local", engine.UnrealEngineError),
    ],
)
def test_unreal_engine_dir_exists(unreal_engine,raises,request):
    unreal_engine = request.getfixturevalue(unreal_engine)
    if raises is not None:
        with pytest.raises(raises):
            assert engine.UnrealEngine.engine_dir_exists(unreal_engine)
    else:
        assert engine.UnrealEngine.engine_dir_exists(unreal_engine) is None



def test_unreal_engine_dir_exist_types():
    with pytest.raises(TypeError):
        assert engine.UnrealEngine.engine_dir_exists(None)

@pytest.mark.parametrize(
    "unreal_engine,expected",
    [
        ("engine_empty", False),
        ("engine_empty_version_egl_4_26_2", True),
        ("engine_empty_version_empty", False),
        ("engine_local", False),
    ],
)
def test_unreal_engine_is_installed_build(unreal_engine, expected, request):
    unreal_engine = request.getfixturevalue(unreal_engine)
    assert unreal_engine.is_installed_build() is expected


@pytest.mark.parametrize(
    "unreal_engine,expected",
    [
        ("engine_empty", False),
        ("engine_empty_version_egl_4_26_2", False),
        ("engine_empty_version_empty", True),
        ("engine_local", False),
    ],
)
def test_unreal_engine_is_source_build(unreal_engine, expected, request):
    unreal_engine = request.getfixturevalue(unreal_engine)
    assert unreal_engine.is_source_build() is expected


@pytest.mark.parametrize(
    "unreal_path,raises,expected",
    [
        ("", engine.UnrealEngineError, None),
        ("/", engine.UnrealEngineError, None),
        ("/Game", engine.UnrealEngineError, None),
        ("/Game/whatever", engine.UnrealEngineError, None),
        ("/Engine", engine.UnrealEngineError, None),
        ("/Engine/whatever", None, os.path.realpath(os.path.join(".","Engine","Content","whatever.uasset"))),
        ("/Invalid", engine.UnrealEngineError, None),
        ("/Invalid/whatever", engine.UnrealEngineError, None),
        ("/test", engine.UnrealEngineError, None),
        ("/test/whatever", engine.UnrealEngineError, None),
    ],
)
def test_unreal_path_to_file_path(
    unreal_path, raises, expected, engine_local
):
    if raises:
        with pytest.raises(raises):
            assert (
                engine_local.unreal_path_to_file_path(unreal_path)
                == expected
            )
    else:
        assert (
            engine_local.unreal_path_to_file_path(unreal_path) == expected
        )

@pytest.mark.parametrize(
    "file_path,raises,expected",
    [
        ("", engine.UnrealEngineError, None),
        ("/", engine.UnrealEngineError, None),
        (".", engine.UnrealEngineError, None),
        (os.path.realpath("./Engine"), engine.UnrealEngineError, None),
        (os.path.realpath("./Engine/Content"), None, "/Engine/"),
        (
            os.path.realpath(os.path.join(".", "Engine", "Content", "whatever.uasset")),
            None,
            "/Engine/whatever",
        ),
    ],
)
def test_unreal_path_from_file_path(
    file_path, raises, expected, engine_local
):
    if raises:
        with pytest.raises(raises):
            assert (
                engine_local.unreal_path_from_file_path(
                    file_path
                )
                == expected
            )
    else:
        assert (
            engine_local.unreal_path_from_file_path(file_path)
            == expected
        )
