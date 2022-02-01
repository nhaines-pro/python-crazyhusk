"""Object wrappers for working with Unreal Engine installations."""
import glob
import json
import os
import platform
import winreg
import pkg_resources


def find_egl_engines_windows():
    """Find and yield all Epic Games Launcher engines."""
    if platform.system() != "Windows":
        return
    print("Finding Epic Games Launcher installations for Windows platform...")
    dat_file = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"
    if os.path.isfile(dat_file):
        with open(dat_file, encoding="utf-8") as _datfile:
            for item in json.load(_datfile).get("InstallationList", []):
                yield item.get("InstallLocation")

    # check legacy paths
    for ue_dir in glob.iglob(r"C:\Program Files\Epic Games\UE_*"):
        yield ue_dir


def find_registered_engines_windows():
    """Find and yield all engines associated via Windows Registry keys."""
    if platform.system() != "Windows":
        return

    print("Finding Windows Registry installations...")
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Epic Games\Unreal Engine\Builds"
        ) as key:
            for i in range(1024):
                _key, _value, _type = winreg.EnumValue(key, i)
                yield os.path.abspath(os.path.join(_value, "Engine"))
    except OSError:
        return


def list_engines():
    """Print all found engines."""
    print("Listing all the engines...")
    for entry_point in pkg_resources.iter_entry_points("crazyhusk.find_engines"):
        for engine in entry_point.load()():
            print(engine)
