"""Object wrappers for working with Unreal Engine installations."""
import json
import os
import pkg_resources
import platform


def find_egl_engines_windows():
    """Find and yeild all Epic Games Launcher engines."""
    if platform.system() != "Windows":
        return
    print(f"Finding Epic Games Launcher installations for Windows platform...")
    DAT_FILE = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"
    if os.path.isfile(DAT_FILE):
        with open(DAT_FILE) as _datfile:
            for item in json.load(_datfile).get("InstallationList", []):
                yield item.get("InstallLocation")


def list_engines():
    print("Listing all the engines...")
    for entry_point in pkg_resources.iter_entry_points("crazyhusk.find_engines"):
        for engine in entry_point.load()():
            print(engine)
