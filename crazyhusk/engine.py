"""Object wrappers for working with Unreal Engine installations."""
import json
import os
import platform
import pkg_resources


def find_egl_engines_windows():
    """Find and yeild all Epic Games Launcher engines."""
    if platform.system() != "Windows":
        return
    print("Finding Epic Games Launcher installations for Windows platform...")
    dat_file = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"
    if os.path.isfile(dat_file):
        with open(dat_file, encoding="utf-8") as _datfile:
            for item in json.load(_datfile).get("InstallationList", []):
                yield item.get("InstallLocation")


def list_engines():
    """Print all found engines."""
    print("Listing all the engines...")
    for entry_point in pkg_resources.iter_entry_points("crazyhusk.find_engines"):
        for engine in entry_point.load()():
            print(engine)
