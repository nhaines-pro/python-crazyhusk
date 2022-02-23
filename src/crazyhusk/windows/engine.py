"""Windows platform extensions for UnrealEngine objects."""
# Standard Library
import json
import logging
import os
import platform
from typing import Iterable, Optional

# CrazyHusk
from crazyhusk.engine import UnrealEngine

DAT_FILE = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"


def find_egl_engine_windows(association: str) -> Optional[UnrealEngine]:
    """Find Epic Games Launcher engine distribution from EngineAssociation string."""
    if platform.system() != "Windows":
        return None

    if os.path.isfile(DAT_FILE):
        with open(DAT_FILE, encoding="utf-8") as _datfile:
            for item in json.load(_datfile).get("InstallationList", []):
                if (
                    association == item.get("InstallLocation")
                    or association == item.get("AppVersion", "").split("-")[0][:-2]
                ):
                    return UnrealEngine(
                        item.get("InstallLocation"),
                        item.get("AppVersion", "").split("-")[0][:-2],
                    )
    return None


def find_registered_engines_windows(association: str) -> Optional[UnrealEngine]:
    """Find Windows Registry engine distribution from EngineAssociation string."""
    if platform.system() != "Windows":
        return None

    try:
        # Standard Library
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Epic Games\Unreal Engine\Builds"
        ) as key:
            base_dir, _ = winreg.QueryValueEx(key, association)
            return UnrealEngine(os.path.join(base_dir, "Engine"), association)
    except (OSError, ModuleNotFoundError):
        return None


def list_egl_engines_windows() -> Iterable[UnrealEngine]:
    """List all Epic Games Launcher engines."""
    if platform.system() != "Windows":
        return

    logging.info("Gathering Epic Games Launcher installations for Windows platform...")
    if os.path.isfile(DAT_FILE):
        with open(DAT_FILE, encoding="utf-8") as _datfile:
            for item in json.load(_datfile).get("InstallationList", []):
                yield UnrealEngine(
                    item.get("InstallLocation"),
                    item.get("AppVersion", "").split("-")[0][:-2],
                )


def list_registered_engines_windows() -> Iterable[UnrealEngine]:
    """List all engines associated via Windows Registry keys."""
    if platform.system() != "Windows":
        return

    logging.info("Gathering Windows Registry installations...")
    try:
        # Standard Library
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Epic Games\Unreal Engine\Builds"
        ) as key:
            for i in range(1024):
                _key, _value, _type = winreg.EnumValue(key, i)
                yield UnrealEngine(os.path.abspath(_value), _key)
    except (OSError, ModuleNotFoundError):
        return


def resolve_executable_path_windows(
    engine: UnrealEngine, executable_name: str
) -> Optional[str]:
    """Resolve an expected real path for a given executable name."""
    if platform.system() != "Windows":
        return None

    if not isinstance(engine, UnrealEngine):
        raise TypeError(
            f"Must provide an instance of crazyhusk.engine.UnrealEngine, got: {engine!r}"
        )

    executable_name = executable_name.lower()
    if executable_name == "automationtool":
        return os.path.realpath(
            os.path.join(engine.engine_dir, "Binaries", "DotNet", "AutomationTool.exe")
        )
    elif executable_name == "swarmagent":
        return os.path.realpath(
            os.path.join(engine.engine_dir, "Binaries", "DotNET", "SwarmAgent.exe")
        )
    elif executable_name == "swarmcoordinator":
        return os.path.realpath(
            os.path.join(
                engine.engine_dir, "Binaries", "DotNET", "SwarmCoordinator.exe"
            )
        )
    elif executable_name == "unrealbuildtool":
        return os.path.realpath(
            os.path.join(engine.engine_dir, "Binaries", "DotNET", "UnrealBuildTool.exe")
        )
    elif executable_name == "ue4editor":
        return os.path.realpath(
            os.path.join(engine.engine_dir, "Binaries", "Win64", "UE4Editor.exe")
        )
    elif executable_name == "ue4editor-cmd":
        return os.path.realpath(
            os.path.join(engine.engine_dir, "Binaries", "Win64", "UE4Editor-Cmd.exe")
        )
    elif executable_name == "unrealpak":
        return os.path.realpath(
            os.path.join(engine.engine_dir, "Binaries", "Win64", "UnrealPak.exe")
        )
    return None
