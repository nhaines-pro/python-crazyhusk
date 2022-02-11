"""Windows platform extensions for UnrealEngine objects."""
# Standard Library
import glob
import json
import logging
import os
import platform

# CrazyHusk
from crazyhusk.engine import UnrealEngine

DAT_FILE = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"


def find_egl_engine_windows(association):
    """Find Epic Games Launcher engine distribution from EngineAssociation string."""
    if platform.system() != "Windows":
        return

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


def find_registered_engines_windows(association):
    """Find Windows Registry engine distribution from EngineAssociation string."""
    if platform.system() != "Windows":
        return

    try:
        # Standard Library
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Epic Games\Unreal Engine\Builds"
        ) as key:
            base_dir, _ = winreg.QueryValueEx(key, association)
            return UnrealEngine(os.path.join(base_dir, "Engine"), association)
    except OSError:
        return


def list_egl_engines_windows():
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

    # check legacy paths
    for ue_dir in glob.iglob(r"C:\Program Files\Epic Games\UE_*"):
        yield UnrealEngine(ue_dir, ue_dir.split("UE_")[-1])


def list_registered_engines_windows():
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
    except OSError:
        return
