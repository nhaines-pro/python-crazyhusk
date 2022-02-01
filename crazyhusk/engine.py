"""Object wrappers for working with Unreal Engine installations."""
import glob
import json
import logging
import os
import platform
import winreg

import pkg_resources


__all__ = ["UnrealEngine", "UnrealEngineError"]


class UnrealEngineError(Exception):
    """Custom exception representing errors encountered with UnrealEngine."""


class UnrealEngine(object):
    """Object wrapper representing an Unreal Engine."""

    def __init__(self, base_dir, association_name=None):
        """Initialize a new UnrealEngine."""
        if base_dir is None:
            raise UnrealEngineError("UnrealEngine base directory must not be None.")
        elif base_dir == "":
            raise UnrealEngineError("UnrealEngine base directory must not be empty.")

        self.base_dir = base_dir
        self.association_name = association_name

    def __repr__(self):
        """Python interpreter representation of this instance."""
        return f"<UnrealEngine {self.association_name} at {self.base_dir}>"

    def __lt__(self, other):
        return self.association_name < other.association_name

    @property
    def engine_dir(self):
        """Path to this Engine's Engine directory."""
        return os.path.join(self.base_dir, "Engine")

    @property
    def feature_packs_dir(self):
        """Path to this Engine's FeaturePacks directory."""
        return os.path.join(self.base_dir, "FeaturePacks")

    @property
    def samples_dir(self):
        """Path to this Engine's Samples directory."""
        return os.path.join(self.base_dir, "Samples")

    @property
    def templates_dir(self):
        """Path to this Engine's Templates directory."""
        return os.path.join(self.base_dir, "Templates")

    @property
    def build_dir(self):
        """Path to this Engine's Binaries directory."""
        return os.path.join(self.base_dir, "Engine", "Build")

    @property
    def config_dir(self):
        """Path to this Engine's Config directory."""
        return os.path.join(self.base_dir, "Engine", "Config")

    @property
    def content_dir(self):
        """Path to this Engine's Content directory."""
        return os.path.join(self.base_dir, "Engine", "Content")

    @property
    def plugins_dir(self):
        """Path to this Engine's Plugins directory."""
        return os.path.join(self.base_dir, "Engine", "Plugins")

    @staticmethod
    def list_engines():
        """Log all found engines."""
        logging.info("Listing all the engines...")
        for engine in sorted(UnrealEngine.find_all_engines()):
            logging.info(engine)

    @staticmethod
    def find_all_engines():
        """Find and yield all available engine installations."""
        for entry_point in pkg_resources.iter_entry_points("crazyhusk.find_engines"):
            for engine in entry_point.load()():
                yield engine


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
