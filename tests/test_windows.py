# Standard Library
import json

# Third Party
import pytest

# CrazyHusk
import crazyhusk.windows
from crazyhusk.engine import UnrealEngine
from crazyhusk.windows import engine


@pytest.fixture(scope="function")
def basic_datfile(tmp_path):
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


@pytest.fixture(scope="function")
def engine_local():
    yield engine.UnrealEngine(".")


def test_find_egl_engine_windows_no_datfile(tmp_path, monkeypatch):
    dat_file = tmp_path / "LauncherInstalled.dat"
    engine.DAT_FILE = dat_file
    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    assert engine.find_egl_engine_windows("") is None
    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert engine.find_egl_engine_windows("") is None


def test_find_egl_engine_windows_with_datfile(basic_datfile, tmp_path, monkeypatch):
    dat_file = tmp_path / "LauncherInstalled.dat"
    dat_file.write_text(basic_datfile)
    engine.DAT_FILE = dat_file

    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    assert engine.find_egl_engine_windows("4.26") is None

    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert isinstance(engine.find_egl_engine_windows("4.26"), UnrealEngine)
    assert engine.find_egl_engine_windows("4.27") is None


def test_list_egl_engine_windows_no_datfile(tmp_path, monkeypatch):
    dat_file = tmp_path / "LauncherInstalled.dat"
    engine.DAT_FILE = dat_file
    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    for _engine in engine.list_egl_engines_windows():
        assert _engine is None
    monkeypatch.setattr("platform.system", lambda: "Windows")
    for _engine in engine.list_egl_engines_windows():
        assert _engine is None


def test_list_egl_engine_windows_with_datfile(basic_datfile, tmp_path, monkeypatch):
    dat_file = tmp_path / "LauncherInstalled.dat"
    dat_file.write_text(basic_datfile)
    engine.DAT_FILE = dat_file
    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    for _engine in engine.list_egl_engines_windows():
        assert _engine is None
    monkeypatch.setattr("platform.system", lambda: "Windows")
    for _engine in engine.list_egl_engines_windows():
        assert isinstance(_engine, UnrealEngine)


def test_registry_nonwindows(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "NotWindows")
    assert engine.find_registered_engines_windows("random_string") is None
    assert len(list(engine.list_registered_engines_windows())) == 0


def test_registry_windows(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert engine.find_registered_engines_windows("random_string") is None
    assert len(list(engine.list_registered_engines_windows())) == 0


def test_resolve_executable_path_windows(monkeypatch, engine_local):
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
