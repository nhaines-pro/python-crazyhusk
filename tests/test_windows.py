# Standard Library
from typing import Any

# Third Party
import pytest

# CrazyHusk
import crazyhusk.windows
from crazyhusk.engine import UnrealEngine
from crazyhusk.windows import engine


def test_find_egl_engine_windows_no_datfile(tmp_path: Any, monkeypatch: Any) -> None:
    dat_file = tmp_path / "LauncherInstalled.dat"
    engine.DAT_FILE = dat_file
    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    assert engine.find_egl_engine_windows("") is None
    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert engine.find_egl_engine_windows("") is None


def test_find_egl_engine_windows_with_datfile(
    basic_datfile: str, tmp_path: Any, monkeypatch: Any
) -> None:
    dat_file = tmp_path / "LauncherInstalled.dat"
    dat_file.write_text(basic_datfile)
    engine.DAT_FILE = dat_file

    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    assert engine.find_egl_engine_windows("4.26") is None

    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert isinstance(engine.find_egl_engine_windows("4.26"), UnrealEngine)
    assert engine.find_egl_engine_windows("4.27") is None


def test_list_egl_engine_windows_no_datfile(tmp_path: Any, monkeypatch: Any) -> None:
    dat_file = tmp_path / "LauncherInstalled.dat"
    engine.DAT_FILE = dat_file
    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    for _engine in engine.list_egl_engines_windows():
        assert _engine is None
    monkeypatch.setattr("platform.system", lambda: "Windows")
    for _engine in engine.list_egl_engines_windows():
        assert _engine is None


def test_list_egl_engine_windows_with_datfile(
    basic_datfile: str, tmp_path: Any, monkeypatch: Any
) -> None:
    dat_file = tmp_path / "LauncherInstalled.dat"
    dat_file.write_text(basic_datfile)
    engine.DAT_FILE = dat_file
    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    for _engine in engine.list_egl_engines_windows():
        assert _engine is None
    monkeypatch.setattr("platform.system", lambda: "Windows")
    for _engine in engine.list_egl_engines_windows():
        assert isinstance(_engine, UnrealEngine)


def test_registry_nonwindows(monkeypatch: Any, mock_winreg: Any) -> None:
    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    assert engine.find_registered_engines_windows("random_string") is None
    assert len(list(engine.list_registered_engines_windows())) == 0


def test_registry_windows(monkeypatch: Any, mock_winreg: Any) -> None:
    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert engine.find_registered_engines_windows("random_string") is None
    assert len(list(engine.list_registered_engines_windows())) == 0


def test_resolve_executable_path_windows(
    monkeypatch: Any, engine_local: engine.UnrealEngine
) -> None:
    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    assert engine.resolve_executable_path_windows(None, None) is None
    monkeypatch.setattr("platform.system", lambda: "Windows")
    with pytest.raises(TypeError):
        assert engine.resolve_executable_path_windows(None, None) is None

    with pytest.raises(AttributeError):
        assert engine.resolve_executable_path_windows(engine_local, None) is None

    assert engine.resolve_executable_path_windows(engine_local, "") is None
    assert engine.resolve_executable_path_windows(engine_local, "random_string") is None
    assert (
        engine.resolve_executable_path_windows(engine_local, "AutomationTool")
        is not None
    )
    assert (
        engine.resolve_executable_path_windows(engine_local, "automationtool")
        is not None
    )
    assert (
        engine.resolve_executable_path_windows(engine_local, "swarmagent") is not None
    )
    assert (
        engine.resolve_executable_path_windows(engine_local, "swarmcoordinator")
        is not None
    )
    assert (
        engine.resolve_executable_path_windows(engine_local, "unrealbuildtool")
        is not None
    )
    assert engine.resolve_executable_path_windows(engine_local, "ue4editor") is not None
    assert (
        engine.resolve_executable_path_windows(engine_local, "ue4editor-cmd")
        is not None
    )
    assert engine.resolve_executable_path_windows(engine_local, "unrealpak") is not None
