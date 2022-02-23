"""Logging utilities for crazyhusk Unreal Engine object wrappers."""
# Standard Library
import calendar
import logging
import re
from datetime import datetime
from typing import Any

try:
    # Standard Library
    from typing import Literal  # type:ignore
except ImportError:
    # Third Party
    from typing_extensions import Literal  # type:ignore

# Regular expression for capturing data from UE4 logs
RE_UE4_LOG_LINE = re.compile(
    r"\[(?P<timestamp>[\d.:\-]+)\]\[.+\](?P<module>\w+): ?((?P<level>(Display)|(Info)|(Warning)|(Error)): ?)?(?P<message>.+)$"
)
RE_UBT_LOG_LINE = re.compile(
    r"^(?P<filename>.+?)\((?P<linenumber>\d+),?(?P<colnumber>\d+?)?\)\s?\:\s?(((?P<level>error|warning) \w+)|note)\:\s(?P<message>.+?)$"
)

UE4_LOG_MAP = {
    "Info": logging.INFO,
    "Display": logging.INFO,
    "Warning": logging.WARNING,
    "Error": logging.ERROR,
}

UBT_LOG_MAP = {"warning": logging.WARNING, "error": logging.ERROR}


class FilterEngineRun(logging.Filter):
    """Filter to enhance log records when using UnrealEngine.run()."""

    def __init__(self, executable: str, *args: str) -> None:
        """Initialize the filter base args."""
        logging.Filter.__init__(self)
        self.executable: str = executable
        self.cmd_args = args

    def filter(self, record: Any) -> Literal[True]:
        """Enhance a loggable record's attributes."""
        record.executable = self.executable
        record.cmd_args = self.cmd_args
        return True


class FilterUBTWarnings(logging.Filter):
    """Filter to enhance log records generated by UnrealBuildTool."""

    def filter(self, record: Any) -> Literal[True]:
        """Filter LogRecords emitted from UnrealBuildTool which are warnings/errors/notes."""
        captured = RE_UBT_LOG_LINE.match(record.msg)
        if captured is not None:
            record.levelno = UBT_LOG_MAP.get(captured.group("level"), logging.WARN)
            record.levelname = logging.getLevelName(record.levelno)
            record.filename = captured.group("filename")
            record.linenumber = captured.group("linenumber")
            record.colnumber = captured.group("colnumber")
            record.sub_msg = captured.group("message")
        return True


class FilterUE4Logs(logging.Filter):
    """Filter to enhance log records generated by UE4Editor/UE4Game."""

    def filter(self, record: Any) -> Literal[True]:
        """Filter LogRecords emitted from UE4Editor/UE4Game."""
        captured = RE_UE4_LOG_LINE.match(record.msg)
        if captured is not None:
            record.levelno = UE4_LOG_MAP.get(captured.group("level"), logging.INFO)
            record.levelname = logging.getLevelName(record.levelno)
            record.created = calendar.timegm(
                datetime.strptime(
                    captured.group("timestamp"), "%Y.%m.%d-%H.%M.%S:%f"
                ).timetuple()
            )
            record.module = captured.group("module")
            record.sub_msg = captured.group("message")
        return True
