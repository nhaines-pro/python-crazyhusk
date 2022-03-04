# Standard Library
import json
from typing import Any, Dict, List, Optional, Type
from xml.etree.ElementTree import Element

# Third Party
import pytest
from pyexpat import ExpatError

# CrazyHusk
from crazyhusk import reports


@pytest.mark.parametrize(
    "timestamp,raises,expected",
    [
        (None, TypeError, None),
        (123, TypeError, None),
        ("", ValueError, None),
        ("123456", ValueError, None),
        ("1234.56.78-12.34.56", ValueError, None),
        ("2022.02.24-14.02.39", None, "2022-02-24T14:02:39"),
    ],
)
def test_report_timestamp_to_iso8601_timestamp(
    timestamp: Any, raises: Optional[Type[BaseException]], expected: Optional[str]
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert reports.report_timestamp_to_iso8601_timestamp(timestamp) is None
    else:
        assert reports.report_timestamp_to_iso8601_timestamp(timestamp) == expected


@pytest.mark.parametrize(
    "entry,raises",
    [
        (None, AttributeError),
        ("", AttributeError),
        ({}, None),
        ({"timestamp": None}, None),
        ({"timestamp": ""}, ValueError),
        ({"timestamp": "123456"}, ValueError),
        ({"timestamp": "1234.56.78-12.34.56"}, ValueError),
        ({"timestamp": "2022.02.24-14.02.39"}, None),
    ],
)
def test_report_entry_to_entry_xml(
    entry: Dict[str, Any], raises: Optional[Type[BaseException]]
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert isinstance(reports.report_entry_to_entry_xml(entry), Element)
    else:
        assert isinstance(reports.report_entry_to_entry_xml(entry), Element)


@pytest.mark.parametrize(
    "test,raises",
    [
        (None, AttributeError),
        ("", AttributeError),
        ({}, None),
        ({"entries": None}, TypeError),
        ({"entries": ""}, None),
        ({"entries": "randomstring"}, AttributeError),
        ({"entries": []}, None),
        ({"entries": [{}]}, None),
        ({"entries": [{"timestamp": None}]}, None),
        ({"entries": [{"timestamp": ""}]}, ValueError),
        ({"entries": [{"timestamp": "2022.02.24-14.02.39"}]}, None),
    ],
)
def test_report_test_to_testcase_xml(
    test: Dict[str, Any], raises: Optional[Type[BaseException]]
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert isinstance(reports.report_test_to_testcase_xml(test), Element)
    else:
        assert isinstance(reports.report_test_to_testcase_xml(test), Element)


@pytest.mark.parametrize(
    "report,raises",
    [
        (None, AttributeError),
        ("", AttributeError),
        ({}, None),
        ({"reportCreatedOn": None}, None),
        ({"reportCreatedOn": ""}, ValueError),
        ({"reportCreatedOn": "123456"}, ValueError),
        ({"reportCreatedOn": "1234.56.78-12.34.56"}, ValueError),
        ({"reportCreatedOn": "2022.02.24-14.02.39"}, None),
        ({"tests": None}, TypeError),
        ({"tests": ""}, None),
        ({"tests": "randomstring"}, AttributeError),
        ({"tests": []}, None),
        ({"tests": [{}]}, None),
    ],
)
def test_report_object_to_testsuite_xml(
    report: Dict[str, Any], raises: Optional[Type[BaseException]]
) -> None:
    if raises is not None:
        with pytest.raises(raises):
            assert isinstance(reports.report_object_to_testsuite_xml(report), Element)
    else:
        assert isinstance(reports.report_object_to_testsuite_xml(report), Element)


@pytest.mark.parametrize(
    "report_file_fixture,raises",
    [
        ("null_report_file", TypeError),
        ("empty_filename_report_file", ValueError),
        ("non_json_report_file", ValueError),
        ("empty_json_report_file", json.JSONDecodeError),
        ("list_json_report_file", ValueError),
    ],
)
def test_json_report_to_dict(
    report_file_fixture: str, raises: Optional[Type[BaseException]], request: Any
) -> None:
    report_file = request.getfixturevalue(report_file_fixture)
    if raises is not None:
        with pytest.raises(raises):
            assert isinstance(reports.json_report_to_dict(report_file), dict)
    else:
        assert isinstance(reports.json_report_to_dict(report_file), dict)


@pytest.mark.parametrize(
    "report_file_fixture,test_suites_fixture,raises",
    [
        ("null_report_file", "null_test_suites", TypeError),
        ("empty_filename_report_file", "emptystring_test_suites", ValueError),
        ("xml_filename_report_file", "emptystring_test_suites", AttributeError),
        ("xml_filename_mkdirs_report_file", "emptystring_test_suites", AttributeError),
        ("xml_filename_report_file", "empty_element_test_suites", ExpatError),
        ("xml_filename_report_file", "basic_element_test_suites", None),
    ],
)
def test_write_junit_xml_report(
    report_file_fixture: str,
    test_suites_fixture: str,
    raises: Optional[Type[BaseException]],
    request: Any,
) -> None:
    report_file = request.getfixturevalue(report_file_fixture)
    test_suites = request.getfixturevalue(test_suites_fixture)
    if raises is not None:
        with pytest.raises(raises):
            assert reports.write_junit_xml_report(report_file, test_suites) is None
    else:
        assert reports.write_junit_xml_report(report_file, test_suites) is None


@pytest.mark.parametrize(
    "report_file_fixture,json_file_fixtures,raises",
    [
        ("null_report_file", ["empty_dict_json_report_file"], TypeError),
        ("empty_filename_report_file", ["empty_dict_json_report_file"], ValueError),
        ("xml_filename_report_file", ["empty_dict_json_report_file"], None),
    ],
)
def test_json_reports_to_junit_xml(
    report_file_fixture: str,
    json_file_fixtures: List[str],
    raises: Optional[Type[BaseException]],
    request: Any,
) -> None:
    report_file = request.getfixturevalue(report_file_fixture)
    json_reports = [
        request.getfixturevalue(json_report) for json_report in json_file_fixtures
    ]
    if raises is not None:
        with pytest.raises(raises):
            assert reports.json_reports_to_junit_xml(report_file, *json_reports) is None
    else:
        assert reports.json_reports_to_junit_xml(report_file, *json_reports) is None
