"""Unit tests for the validated per-type condition accessors in ``_helpers``."""

from azure_functions_doctor.handlers._helpers import (
    CompareVersionParams,
    PackageParams,
    SourceCodeParams,
    parse_compare_version,
    parse_package,
    parse_source_code,
    parse_target,
)


class TestParseTarget:
    def test_returns_target_when_present(self) -> None:
        assert parse_target({"target": "python"}) == "python"

    def test_returns_none_when_missing(self) -> None:
        assert parse_target({}) is None

    def test_returns_none_when_empty(self) -> None:
        assert parse_target({"target": ""}) is None

    def test_returns_none_when_not_str(self) -> None:
        assert parse_target({"target": 123}) is None  # type: ignore[typeddict-item]


class TestParseCompareVersion:
    def test_returns_params_when_complete(self) -> None:
        result = parse_compare_version({"target": "python", "operator": ">=", "value": "3.10"})
        assert result == CompareVersionParams("python", ">=", "3.10")

    def test_returns_none_when_missing_operator(self) -> None:
        assert parse_compare_version({"target": "python", "value": "3.10"}) is None

    def test_returns_none_when_missing_target(self) -> None:
        assert parse_compare_version({"operator": ">=", "value": "3.10"}) is None

    def test_returns_none_when_missing_value(self) -> None:
        assert parse_compare_version({"target": "python", "operator": ">="}) is None


class TestParseSourceCode:
    def test_returns_params_with_default_mode(self) -> None:
        assert parse_source_code({"keyword": "@app."}) == SourceCodeParams("@app.", "string")

    def test_returns_params_with_explicit_mode(self) -> None:
        assert parse_source_code({"keyword": "@app.", "mode": "ast"}) == SourceCodeParams(
            "@app.", "ast"
        )

    def test_returns_none_when_keyword_missing(self) -> None:
        assert parse_source_code({}) is None

    def test_returns_none_when_keyword_not_str(self) -> None:
        assert parse_source_code({"keyword": 5}) is None  # type: ignore[typeddict-item]


class TestParsePackage:
    def test_returns_package_field(self) -> None:
        assert parse_package({"package": "azure-functions"}) == PackageParams(
            "azure-functions", "requirements.txt"
        )

    def test_falls_back_to_target(self) -> None:
        assert parse_package({"target": "azure-functions"}) == PackageParams(
            "azure-functions", "requirements.txt"
        )

    def test_uses_custom_file(self) -> None:
        assert parse_package({"package": "azure-functions", "file": "reqs.txt"}) == PackageParams(
            "azure-functions", "reqs.txt"
        )

    def test_returns_none_when_absent(self) -> None:
        assert parse_package({}) is None
