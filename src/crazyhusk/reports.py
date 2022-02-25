"""Utilities for working with report formats generated by Unreal Engine."""

# Standard Library
import datetime
import json
import os
from typing import Any, Dict, List
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


def report_timestamp_to_iso8601_timestamp(timestamp: str) -> str:
    return datetime.datetime.strptime(timestamp, "%Y.%m.%d-%H.%M.%S").isoformat()


def report_entry_to_entry_xml(entry: Dict[str, Any]) -> Element:
    failure = Element("failure")
    failure.set("type", entry.get("event", {}).get("type", ""))
    failure.set(
        "timestamp", report_timestamp_to_iso8601_timestamp(entry.get("timestamp", ""))
    )
    failure.set(
        "message",
        f'{entry.get("filename","")}:{entry.get("lineNumber","")} {entry.get("event",{}).get("message","")}',
    )
    return failure


def report_test_to_testcase_xml(test: Dict[str, Any]) -> Element:
    test_case = Element("testcase")
    test_case.set("name", test.get("testDisplayName", ""))
    test_case.set("classname", test.get("fullTestPath", ""))
    test_case.set("status", test.get("state", ""))
    for entry in test.get("entries", []):
        test_case.append(report_entry_to_entry_xml(entry))
    return test_case


def report_object_to_testsuite_xml(report: Dict[str, Any]) -> Element:
    test_suite = Element("testsuite")
    test_suite.set("tests", str(len(report.get("tests", []))))
    test_suite.set("failures", str(report.get("failed", 0)))
    test_suite.set("skipped", str(report.get("notRun", 0)))
    test_suite.set("time", str(report.get("totalDuration", 0.0)))
    test_suite.set(
        "timestamp",
        report_timestamp_to_iso8601_timestamp(report.get("reportCreatedOn", "")),
    )

    branch, changelist, platform = report.get("clientDescriptor", " -  - ").split(" - ")
    properties = Element("properties")

    branch_property = Element("property")
    branch_property.set("name", "branch")
    branch_property.set("value", branch)
    properties.append(branch_property)

    changelist_property = Element("property")
    changelist_property.set("name", "changelist")
    changelist_property.set("value", changelist)
    properties.append(changelist_property)

    platform_property = Element("property")
    platform_property.set("name", "platform")
    platform_property.set("value", platform)
    properties.append(platform_property)

    test_suite.append(properties)

    for test in report.get("tests", []):
        test_suite.append(report_test_to_testcase_xml(test))

    return test_suite


def json_report_to_dict(report_file: str) -> Dict[str, Any]:
    if not os.path.isfile(report_file):
        raise ValueError(f"JSON report not found: {report_file}")

    if not os.path.splitext(report_file)[-1] == ".json":
        raise ValueError(f"Report file is not JSON: {report_file}")

    with open(report_file, "r", encoding="utf-8-sig") as json_report:
        report_dct = json.load(json_report)
        if not isinstance(report_dct, dict):
            raise ValueError(f"JSON report returns non-object: {report_file}")
        return report_dct


def write_junit_xml_report(report_file: str, test_suites: Element) -> None:
    if not os.path.splitext(report_file)[-1] == ".xml":
        raise ValueError(f"Report file is not XML: {report_file}")

    report_dir = os.path.dirname(report_file)
    if not os.path.isdir(report_dir):
        os.makedirs(report_dir, exist_ok=True)

    with open(report_file, "w", encoding="utf-8") as xml_report:
        xml_report.write(
            minidom.parseString(ElementTree.tostring(test_suites, "utf-8")).toprettyxml(
                indent=" " * 4
            )
        )


def json_reports_to_junit_xml(junit_report: str, *json_reports: str) -> None:
    """Convert a JSON report from Unreal automation to jUnit XML format."""
    test_suites = Element("testsuites")
    test_suites.set("name", "Unreal Automation Tests")

    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_time = 0.0
    for report in json_reports:
        test_suite = report_object_to_testsuite_xml(json_report_to_dict(report))
        test_suite.set("name", os.path.splitext(os.path.basename(report))[0])
        total_tests += int(test_suite.get("tests", 0))
        total_failures += int(test_suite.get("failures", 0))
        total_errors += int(test_suite.get("errors", 0))
        total_time += float(test_suite.get("time", 0.0))
        test_suites.append(test_suite)

    test_suites.set("tests", str(total_tests))
    test_suites.set("failures", str(total_failures))
    test_suites.set("errors", str(total_errors))
    test_suites.set("time", str(total_time))
    write_junit_xml_report(junit_report, test_suites)
