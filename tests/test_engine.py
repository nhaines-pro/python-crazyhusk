# Standard Library
import os
import types
from typing import Any, Dict, Optional, Type

# Third Party
import pytest

# CrazyHusk
from crazyhusk import config, engine
from crazyhusk.code import CodeTemplate
from crazyhusk.plugin import UnrealPlugin


@pytest.mark.parametrize(
    "version_fixture,major,minor,patch,changelist,branch",
    [
        ("version_empty", 4, 0, 0, 0, ""),
        ("version_26_0", 4, 26, 0, 0, ""),
        ("version_26_1", 4, 26, 1, 0, ""),
        ("version_26_1_123456", 4, 26, 1, 123456, ""),
        ("version_26_1_123456_branch", 4, 26, 1, 123456, "++UE4+Release-4.26"),
    ],
)
def test_unreal_version_init(
    version_fixture: str,
    major: int,
    minor: int,
    patch: int,
    changelist: int,
    branch: str,
    request: Any,
) -> None:
    version = request.getfixturevalue(version_fixture)
    assert version.major == major
    assert version.minor == minor
    assert version.patch == patch
    assert version.changelist == changelist
    assert version.branch == branch


@pytest.mark.parametrize(
    "version_fixture,version_string",
    [
        ("version_empty", "4.0"),
        ("version_26_0", "4.26"),
        ("version_26_1", "4.26.1"),
        ("version_26_1_123456", "4.26.1-123456"),
        ("version_26_1_123456_branch", "4.26.1-123456+++UE4+Release-4.26"),
    ],
)
def test_unreal_version_string(
    version_fixture: str, version_string: str, request: Any
) -> None:
    version = request.getfixturevalue(version_fixture)
    assert str(version) == version_string


@pytest.mark.parametrize(
    "version_fixture,version_repr",
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
def test_unreal_version_repr(
    version_fixture: str, version_repr: str, request: Any
) -> None:
    version = request.getfixturevalue(version_fixture)
    assert repr(version) == version_repr


@pytest.mark.parametrize(
    "first_version_fixture,second_version_fixture",
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
def test_unreal_version_lt(
    first_version_fixture: str, second_version_fixture: str, request: Any
) -> None:
    first_version = request.getfixturevalue(first_version_fixture)
    second_version = request.getfixturevalue(second_version_fixture)
    assert first_version < second_version


def test_unreal_version_lt_null(version_empty: engine.UnrealVersion) -> None:
    with pytest.raises(TypeError):
        assert version_empty < None


def test_unreal_version_lt_not(
    version_empty: engine.UnrealVersion, version_5_0: engine.UnrealVersion
) -> None:
    assert not version_5_0 < version_empty


@pytest.mark.parametrize(
    "first_version_fixture,second_version_fixture",
    [
        ("version_empty", "version_empty"),
        ("version_26_0", "version_26_0"),
        ("version_26_1", "version_26_1"),
        ("version_26_1_123456", "version_26_1_123456"),
        ("version_26_1_234567", "version_26_1_234567"),
        ("version_5_0", "version_5_0"),
    ],
)
def test_unreal_version_eq(
    first_version_fixture: str, second_version_fixture: str, request: Any
) -> None:
    first_version = request.getfixturevalue(first_version_fixture)
    second_version = request.getfixturevalue(second_version_fixture)
    assert first_version == second_version


def test_unreal_version_eq_null(version_empty: engine.UnrealVersion) -> None:
    assert version_empty is not None


@pytest.mark.parametrize(
    "dct,version_string",
    [
        ({}, "4.0"),
        ({"MajorVersion": 5}, "5.0"),
        ({"MinorVersion": 26}, "4.26"),
        ({"MinorVersion": 26, "PatchVersion": 1}, "4.26.1"),
    ],
)
def test_unreal_version_to_object(dct: Dict[str, int], version_string: str) -> None:
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
def test_unreal_engine_init(
    base_dir: Optional[str],
    raises: Optional[Type[BaseException]],
    expected: Optional[str],
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert engine.UnrealEngine(base_dir)
    else:
        assert engine.UnrealEngine(base_dir).base_dir == expected


def test_unreal_engine_repr(engine_empty: engine.UnrealEngine) -> None:
    assert (
        repr(engine_empty)
        == f"<UnrealEngine None Build None at {engine_empty.base_dir}>"
    )


def test_unreal_engine_lt_types(
    engine_empty: engine.UnrealEngine, engine_empty_version_empty: engine.UnrealEngine
) -> None:
    with pytest.raises(TypeError):
        assert engine_empty < None
        assert engine_empty < engine_empty_version_empty


def test_unreal_engine_lt(
    engine_empty_version_empty: engine.UnrealEngine,
    engine_empty_version_egl_4_26_2: engine.UnrealEngine,
) -> None:
    assert engine_empty_version_empty < engine_empty_version_egl_4_26_2


def test_unreal_engine_context(engine_empty: engine.UnrealEngine) -> None:
    with engine_empty:
        assert engine_empty


def test_unreal_engine_dir_properties(
    engine_empty_version_egl_4_26_2: engine.UnrealEngine,
) -> None:
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
    "unreal_engine_fixture,expected",
    [
        ("engine_empty", None),
        ("engine_empty_version_egl_4_26_2", "Installed"),
        ("engine_empty_version_empty", "Source"),
    ],
)
def test_unreal_engine_build_type(
    unreal_engine_fixture: str, expected: Optional[str], request: Any
) -> None:
    unreal_engine = request.getfixturevalue(unreal_engine_fixture)
    assert unreal_engine.build_type == expected


@pytest.mark.parametrize(
    "unreal_engine_fixture,executable,raises",
    [
        ("engine_local", None, TypeError),
        ("engine_local", ".", None),
        ("engine_local", "/bin/scary_dir/important_exe", engine.UnrealExecutionError),
        ("engine_local", os.path.realpath(".."), engine.UnrealExecutionError),
    ],
)
def test_unreal_engine_exe_common_path(
    unreal_engine_fixture: str,
    executable: Optional[str],
    raises: Optional[Type[BaseException]],
    request: Any,
) -> None:
    unreal_engine = request.getfixturevalue(unreal_engine_fixture)
    if raises is not None:
        with pytest.raises(raises):
            assert engine.UnrealEngine.engine_exe_common_path(unreal_engine, executable)
    else:
        assert (
            engine.UnrealEngine.engine_exe_common_path(unreal_engine, executable)
            is None
        )


def test_unreal_engine_exe_common_path_types() -> None:
    with pytest.raises(TypeError):
        assert engine.UnrealEngine.engine_exe_common_path(None, None)


@pytest.mark.parametrize(
    "unreal_engine_fixture,executable,raises",
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
def test_unreal_engine_exe_exists(
    unreal_engine_fixture: str,
    executable: Optional[str],
    raises: Optional[Type[BaseException]],
    request: Any,
) -> None:
    unreal_engine = request.getfixturevalue(unreal_engine_fixture)
    if raises is not None:
        with pytest.raises(raises):
            assert engine.UnrealEngine.engine_exe_exists(unreal_engine, executable)
    else:
        assert engine.UnrealEngine.engine_exe_exists(unreal_engine, executable) is None


def test_unreal_engine_exe_exists_types() -> None:
    with pytest.raises(TypeError):
        assert engine.UnrealEngine.engine_exe_exists(None, None)


@pytest.mark.parametrize(
    "unreal_engine_fixture,raises",
    [
        ("engine_empty", engine.UnrealEngineError),
        ("engine_empty_version_egl_4_26_2", None),
        ("engine_empty_version_empty", None),
        ("engine_local", engine.UnrealEngineError),
    ],
)
def test_unreal_engine_dir_exists(
    unreal_engine_fixture: str, raises: Optional[Type[BaseException]], request: Any
) -> None:
    unreal_engine = request.getfixturevalue(unreal_engine_fixture)
    if raises is not None:
        with pytest.raises(raises):
            assert engine.UnrealEngine.engine_dir_exists(unreal_engine)
    else:
        assert engine.UnrealEngine.engine_dir_exists(unreal_engine) is None


def test_unreal_engine_dir_exist_types() -> None:
    with pytest.raises(TypeError):
        assert engine.UnrealEngine.engine_dir_exists(None)


@pytest.mark.parametrize(
    "unreal_engine_fixture,expected",
    [
        ("engine_empty", False),
        ("engine_empty_version_egl_4_26_2", True),
        ("engine_empty_version_empty", False),
        ("engine_local", False),
    ],
)
def test_unreal_engine_is_installed_build(
    unreal_engine_fixture: str, expected: bool, request: Any
) -> None:
    unreal_engine = request.getfixturevalue(unreal_engine_fixture)
    assert unreal_engine.is_installed_build() is expected


@pytest.mark.parametrize(
    "unreal_engine_fixture,expected",
    [
        ("engine_empty", False),
        ("engine_empty_version_egl_4_26_2", False),
        ("engine_empty_version_empty", True),
        ("engine_local", False),
    ],
)
def test_unreal_engine_is_source_build(
    unreal_engine_fixture: str, expected: bool, request: Any
) -> None:
    unreal_engine = request.getfixturevalue(unreal_engine_fixture)
    assert unreal_engine.is_source_build() is expected


@pytest.mark.parametrize(
    "unreal_path,raises,expected",
    [
        ("", engine.UnrealEngineError, None),
        ("/", engine.UnrealEngineError, None),
        ("/Game", engine.UnrealEngineError, None),
        ("/Game/whatever", engine.UnrealEngineError, None),
        ("/Engine", engine.UnrealEngineError, None),
        (
            "/Engine/whatever",
            None,
            os.path.realpath(os.path.join(".", "Engine", "Content", "whatever.uasset")),
        ),
        ("/Invalid", engine.UnrealEngineError, None),
        ("/Invalid/whatever", engine.UnrealEngineError, None),
        ("/test", engine.UnrealEngineError, None),
        ("/test/whatever", engine.UnrealEngineError, None),
    ],
)
def test_unreal_path_to_file_path(
    unreal_path: str,
    raises: Optional[Type[BaseException]],
    expected: Optional[str],
    engine_local: engine.UnrealEngine,
) -> None:
    if raises:
        with pytest.raises(raises):
            assert engine_local.unreal_path_to_file_path(unreal_path) == expected
    else:
        assert engine_local.unreal_path_to_file_path(unreal_path) == expected


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
    file_path: str,
    raises: Optional[Type[BaseException]],
    expected: Optional[str],
    engine_local: engine.UnrealEngine,
) -> None:
    if raises:
        with pytest.raises(raises):
            assert engine_local.unreal_path_from_file_path(file_path) == expected
    else:
        assert engine_local.unreal_path_from_file_path(file_path) == expected


@pytest.mark.parametrize(
    "unreal_engine_fixture,expected",
    [
        ("engine_empty", {}),
        ("engine_empty_version_egl_4_26_2", {}),
        ("engine_empty_version_empty", {}),
        ("engine_local", {}),
    ],
)
def test_unreal_engine_code_templates(
    unreal_engine_fixture: str, expected: Dict[str, CodeTemplate], request: Any
) -> None:
    unreal_engine = request.getfixturevalue(unreal_engine_fixture)
    assert unreal_engine.code_templates == expected


@pytest.mark.parametrize(
    "unreal_engine_fixture,expected",
    [
        ("engine_empty", {}),
        ("engine_empty_version_egl_4_26_2", {}),
        ("engine_empty_version_empty", {}),
        ("engine_local", {}),
    ],
)
def test_unreal_engine_plugins(
    unreal_engine_fixture: str, expected: Dict[str, UnrealPlugin], request: Any
) -> None:
    unreal_engine = request.getfixturevalue(unreal_engine_fixture)
    assert unreal_engine.plugins == expected


@pytest.mark.parametrize(
    "association,expected",
    [
        ("randomstring", type(None)),
        # TODO: monkeypatch pkg_resources behavior
    ],
)
def test_unreal_engine_find_engine(association: str, expected: Type[Any]) -> None:
    assert type(engine.UnrealEngine.find_engine(association)) == expected


def test_unreal_engine_list_all_engines() -> None:
    assert isinstance(engine.UnrealEngine.list_all_engines(), types.GeneratorType)

    # TODO: monkeypatch pkg_resources behavior
    # assert list(engine.UnrealEngine.list_all_engines())


@pytest.mark.parametrize(
    "unreal_engine_fixture,config_category,platform,expected_count",
    [
        ("engine_empty_version_egl_4_26_2", None, None, 1),
        ("engine_empty_version_egl_4_26_2", "", None, 1),
        ("engine_empty_version_egl_4_26_2", "test", None, 1),
        ("engine_empty_version_egl_4_26_2", "Engine", None, 2),
        ("engine_empty_version_egl_4_26_2", "Engine", "Windows", 4),
    ],
)
def test_unreal_engine_config_files(
    unreal_engine_fixture: str,
    config_category: Optional[str],
    platform: Optional[str],
    expected_count: int,
    request: Any,
) -> None:
    unreal_engine = request.getfixturevalue(unreal_engine_fixture)
    assert (
        len(list(unreal_engine.config_files(config_category, platform)))
        == expected_count
    )


def test_unreal_engine_config(
    engine_empty_version_egl_4_26_2: engine.UnrealEngine,
) -> None:
    assert isinstance(
        engine_empty_version_egl_4_26_2.config(), config.UnrealConfigParser
    )
    assert isinstance(
        engine_empty_version_egl_4_26_2.config("Engine"), config.UnrealConfigParser
    )
    assert isinstance(
        engine_empty_version_egl_4_26_2.config("Engine", "Windows"),
        config.UnrealConfigParser,
    )
