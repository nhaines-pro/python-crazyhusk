# Standard Library
import logging
from typing import Any, Optional, Tuple

# Third Party
import pytest

# CrazyHusk
from crazyhusk import logs


@pytest.mark.parametrize(
    "filter_engine_run_fixture,executable,cmd_args",
    [
        ("null_filter_engine_run", None, ()),
        ("empty_filter_engine_run", "", ()),
        ("one_arg_filter_engine_run", "", ("arg",)),
        (
            "multi_arg_filter_engine_run",
            "",
            (
                "arg1",
                "arg2",
                "arg3",
            ),
        ),
    ],
)
def test_filter_engine_run_init(
    filter_engine_run_fixture: str,
    executable: Optional[str],
    cmd_args: Tuple[str],
    request: Any,
) -> None:
    filter_engine_run = request.getfixturevalue(filter_engine_run_fixture)
    assert filter_engine_run.executable == executable
    assert isinstance(filter_engine_run.cmd_args, tuple)
    assert filter_engine_run.cmd_args == cmd_args


@pytest.mark.parametrize(
    "filter_engine_run_fixture,executable,cmd_args",
    [
        ("null_filter_engine_run", None, ()),
        ("empty_filter_engine_run", "", ()),
        ("one_arg_filter_engine_run", "", ("arg",)),
        (
            "multi_arg_filter_engine_run",
            "",
            (
                "arg1",
                "arg2",
                "arg3",
            ),
        ),
    ],
)
def test_filter_engine_run_filter(
    filter_engine_run_fixture: str,
    executable: Optional[str],
    cmd_args: Tuple[str],
    request: Any,
    caplog: Any,
) -> None:
    filter_engine_run = request.getfixturevalue(filter_engine_run_fixture)
    logger = logging.getLogger("test_filter_engine_run_filter")
    logger.addFilter(filter_engine_run)
    with caplog.at_level(logging.INFO):
        logger.info("test")
        for record in caplog.records:
            assert record.executable == executable
            assert record.cmd_args == cmd_args


@pytest.mark.parametrize(
    "log_string,levelno,levelname,filename,linenumber,colnumber,sub_msg",
    [
        (
            "@progress 'Compiling C++ source code...' 59%",
            logging.INFO,
            "INFO",
            "test_logs.py",
            None,
            None,
            None,
        ),
        (
            "[8/17] MainMenuPlayerController.gen.cpp",
            logging.INFO,
            "INFO",
            "test_logs.py",
            None,
            None,
            None,
        ),
        (
            "/path/to/myfile.cpp(32): error C3861: 'assert': identifier not found",
            logging.ERROR,
            "ERROR",
            "/path/to/myfile.cpp",
            "32",
            None,
            "'assert': identifier not found",
        )
        # TODO: find  appropriate warning message examples, including ones with column numbers
    ],
)
def test_filter_ubt_warnings(
    log_string: str,
    levelno: int,
    levelname: str,
    filename: Optional[str],
    linenumber: Optional[str],
    colnumber: Optional[str],
    sub_msg: Optional[str],
    caplog: Any,
) -> None:
    logger = logging.getLogger("test_filter_ubt_warnings")
    logger.addFilter(logs.FilterUBTWarnings())
    with caplog.at_level(logging.INFO):
        logger.info(log_string)
        for record in caplog.records:
            assert record.levelno == levelno
            assert record.levelname == levelname
            assert record.filename == filename
            if linenumber is not None:
                assert record.linenumber == linenumber
            if colnumber is not None:
                assert record.colnumber == colnumber
            if sub_msg is not None:
                assert record.sub_msg == sub_msg


@pytest.mark.parametrize(
    "log_string,levelno,levelname,created,module,sub_msg",
    [
        (
            "LogPluginManager: Mounting plugin SunPosition",
            logging.INFO,
            "INFO",
            None,
            None,
            None,
        ),
        (
            "[2021.11.29-21.06.49:745][  0]LogConfig: Setting CVar [[r.BloomQuality:5]]",
            logging.INFO,
            "INFO",
            1638220009,
            "LogConfig",
            "Setting CVar [[r.BloomQuality:5]]",
        ),
    ],
)
def test_filter_ue4_logs(
    log_string: str,
    levelno: int,
    levelname: str,
    created: Optional[int],
    module: Optional[str],
    sub_msg: Optional[str],
    caplog: Any,
) -> None:
    logger = logging.getLogger("test_filter_ue4_logs")
    logger.addFilter(logs.FilterUE4Logs())
    with caplog.at_level(logging.INFO):
        logger.info(log_string)
        for record in caplog.records:
            assert record.levelno == levelno
            assert record.levelname == levelname
            if created is not None:
                assert record.created == created
            if module is not None:
                assert record.module == module
            if sub_msg is not None:
                assert record.sub_msg == sub_msg
