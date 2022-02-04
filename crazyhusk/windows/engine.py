"""Windows platform extensions for UnrealEngine objects."""
# Standard Library
import glob
import json
import logging
import os
import platform
import winreg

# CrazyHusk
from crazyhusk.engine import UnrealEngine


def find_egl_engines_windows():
    """Find and yield all Epic Games Launcher engines."""
    if platform.system() != "Windows":
        return

    logging.info("Finding Epic Games Launcher installations for Windows platform...")
    dat_file = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"
    if os.path.isfile(dat_file):
        with open(dat_file, encoding="utf-8") as _datfile:
            for item in json.load(_datfile).get("InstallationList", []):
                yield UnrealEngine(
                    item.get("InstallLocation"),
                    item.get("AppVersion", "").split("-")[0][:-2],
                )

    # check legacy paths
    for ue_dir in glob.iglob(r"C:\Program Files\Epic Games\UE_*"):
        yield UnrealEngine(ue_dir, ue_dir.split("UE_")[-1])


def find_registered_engines_windows():
    """Find and yield all engines associated via Windows Registry keys."""
    if platform.system() != "Windows":
        return

    logging.info("Finding Windows Registry installations...")
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Epic Games\Unreal Engine\Builds"
        ) as key:
            for i in range(1024):
                _key, _value, _type = winreg.EnumValue(key, i)
                yield UnrealEngine(os.path.abspath(_value), _key)
    except OSError:
        return
