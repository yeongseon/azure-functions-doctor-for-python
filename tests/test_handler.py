import json
import sys
import tempfile
from pathlib import Path
from typing import cast

from pytest import MonkeyPatch

from azure_functions_doctor.handlers import Condition, Rule, generic_handler


def test_compare_python_version_pass() -> None:
    """Test that the Python version check passes for the current version."""
    rule: Rule = {
        "type": "compare_version",
        "condition": {
            "target": "python",
            "operator": ">=",
            "value": f"{sys.version_info.major}.{sys.version_info.minor}",
        },
    }
    result = generic_handler(rule, Path("."))
    assert result["status"] == "pass"


def test_compare_python_version_fail() -> None:
    """Test that the Python version check fails for an unsupported version."""
    rule: Rule = {
        "type": "compare_version",
        "condition": {
            "target": "python",
            "operator": ">",
            "value": "99.0",
        },
    }
    result = generic_handler(rule, Path("."))
    assert result["status"] == "fail"


def test_env_var_exists_pass(monkeypatch: MonkeyPatch) -> None:
    """ "Test that the environment variable check passes when the variable is set."""
    monkeypatch.setenv("MY_ENV_VAR", "true")
    rule: Rule = {
        "type": "env_var_exists",
        "condition": {"target": "MY_ENV_VAR"},
    }
    result = generic_handler(rule, Path("."))
    assert result["status"] == "pass"


def test_env_var_exists_fail(monkeypatch: MonkeyPatch) -> None:
    """Test that the environment variable check fails when the variable is not set."""
    monkeypatch.delenv("MY_ENV_VAR", raising=False)
    rule: Rule = {
        "type": "env_var_exists",
        "condition": {"target": "MY_ENV_VAR"},
    }
    result = generic_handler(rule, Path("."))
    assert result["status"] == "fail"


def test_path_exists_pass() -> None:
    """Test that the path exists check passes for sys.executable."""
    rule: Rule = {
        "type": "path_exists",
        "condition": {"target": "sys.executable"},
    }
    result = generic_handler(rule, Path("."))
    assert result["status"] == "pass"


def test_file_exists_pass() -> None:
    """Test that the file exists check passes when the file is present."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.txt"
        file_path.write_text("test")
        rule: Rule = {
            "type": "file_exists",
            "condition": {"target": "test.txt"},
        }
        result = generic_handler(rule, Path(tmpdir))
        assert result["status"] == "pass"


def test_file_exists_fail() -> None:
    """Test that the file exists check fails when the file is not present."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rule: Rule = {
            "type": "file_exists",
            "condition": {"target": "not_found.txt"},
        }
        result = generic_handler(rule, Path(tmpdir))
        assert result["status"] == "fail"


def test_package_installed_pass() -> None:
    """Test that the package installed check passes for an existing package."""
    rule: Rule = {
        "type": "package_installed",
        "condition": {"target": "os"},
    }
    result = generic_handler(rule, Path("."))
    assert result["status"] == "pass"


def test_package_installed_fail() -> None:
    rule: Rule = {
        "type": "package_installed",
        "condition": {"target": "nonexistent_package_zzz"},
    }
    result = generic_handler(rule, Path("."))
    assert result["status"] == "fail"


def test_source_code_contains_pass() -> None:
    """Test that the source code contains check passes when the keyword is found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "sample.py"
        file_path.write_text("# keyword: found")
        rule: Rule = {
            "type": "source_code_contains",
            "condition": {"keyword": "keyword"},
        }
        result = generic_handler(rule, Path(tmpdir))
        assert result["status"] == "pass"


def test_source_code_contains_fail() -> None:
    """Test that the source code contains check fails when the keyword is not found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "sample.py"
        file_path.write_text("# no match here")
        rule: Rule = {
            "type": "source_code_contains",
            "condition": {"keyword": "notfound"},
        }
        result = generic_handler(rule, Path(tmpdir))
        assert result["status"] == "fail"


def test_unknown_check_type() -> None:
    """Test that an unknown check type returns a fail status."""
    rule = cast(
        Rule,
        {
            "type": "unknown_type",
            "id": "invalid_type",
            "label": "Invalid check",
            "section": "misc",
            "category": "misc",
            "condition": {"target": "anything"},
        },
    )

    result = generic_handler(rule, Path("."))

    assert result["status"] == "fail"
    assert "Unknown check type" in result["detail"]


def test_conditional_exists_no_durable_usage_pass() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # No durable usage in source -> check should be skipped/pass
        rule: Rule = {
            "type": "conditional_exists",
            "condition": {"jsonpath": "$.extensions.durableTask"},
        }
        result = generic_handler(rule, Path(tmpdir))
        assert result["status"] == "pass"


def test_conditional_exists_durable_missing_host_fail() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a Python file that contains durable keyword
        file_path = Path(tmpdir) / "function.py"
        file_path.write_text("# uses durable\nfrom azure.durable_functions import DurableOrchestrationContext")

        rule: Rule = {
            "type": "conditional_exists",
            "condition": {"jsonpath": "$.extensions.durableTask"},
        }
        result = generic_handler(rule, Path(tmpdir))
        assert result["status"] == "fail"


def test_conditional_exists_durable_present_pass() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a Python file that contains durable keyword
        file_path = Path(tmpdir) / "function.py"
        file_path.write_text("# uses durable\nfrom azure.durable_functions import DurableOrchestrationContext")
        # Create host.json with the durableTask entry
        host = Path(tmpdir) / "host.json"
        host.write_text('{"extensions": {"durableTask": {}}}')

        rule: Rule = {
            "type": "conditional_exists",
            "condition": {"jsonpath": "$.extensions.durableTask"},
        }
        result = generic_handler(rule, Path(tmpdir))
        assert result["status"] == "pass"


def test_callable_detection_pass_and_fail() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # No ASGI/WSGI files => fail
        rule: Rule = {"type": "callable_detection"}
        result = generic_handler(rule, Path(tmpdir))
        assert result["status"] == "fail"

        # Add a FastAPI example => pass
        file_path = Path(tmpdir) / "app.py"
        file_path.write_text("from fastapi import FastAPI\napp = FastAPI()")
        result2 = generic_handler(rule, Path(tmpdir))
        assert result2["status"] == "pass"


def _make_rule(rule_type: str, condition: Condition) -> Rule:
    # Helper to build a Rule object for new adapter handlers (partial Rule)
    return {"type": rule_type, "condition": condition}  # type: ignore[typeddict-item]


def test_executable_exists_pass_and_fail(tmp_path: Path) -> None:
    # 'sh' should exist on most Unix systems
    rule = _make_rule("executable_exists", {"target": "sh"})
    res = generic_handler(rule, tmp_path)
    assert res["status"] == "pass"

    rule_fail = _make_rule("executable_exists", {"target": "definitely_not_present_abc123"})
    res2 = generic_handler(rule_fail, tmp_path)
    assert res2["status"] == "fail"


def test_any_of_exists_env_and_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    # env var path
    monkeypatch.setenv("AZFUNC_TEST_VAR", "1")
    rule = _make_rule("any_of_exists", {"targets": ["AZFUNC_TEST_VAR"]})
    res = generic_handler(rule, tmp_path)
    assert res["status"] == "pass"

    # file path
    f = tmp_path / "marker.txt"
    f.write_text("ok")
    rule_file = _make_rule("any_of_exists", {"targets": [str(f.name)]})
    res2 = generic_handler(rule_file, tmp_path)
    assert res2["status"] == "pass"

    # none exist
    rule_none = _make_rule("any_of_exists", {"targets": ["nope1", "nope2"]})
    res3 = generic_handler(rule_none, tmp_path)
    assert res3["status"] == "fail"


def test_file_glob_check(tmp_path: Path) -> None:
    # create an unwanted file matching pattern
    bad = tmp_path / "secret.txt"
    bad.write_text("secret")
    rule = _make_rule("file_glob_check", {"patterns": ["secret.txt"]})
    res = generic_handler(rule, tmp_path)
    assert res["status"] == "fail"

    # no matches
    rule_ok = _make_rule("file_glob_check", {"patterns": ["*.doesnotexist"]})
    res2 = generic_handler(rule_ok, tmp_path)
    assert res2["status"] == "pass"


def test_host_json_property_pass_and_fail(tmp_path: Path) -> None:
    host = tmp_path / "host.json"
    host.write_text(json.dumps({"extensionBundle": {"id": "bundle"}}))
    rule = _make_rule("host_json_property", {"jsonpath": "$.extensionBundle"})
    res = generic_handler(rule, tmp_path)
    assert res["status"] == "pass"

    # missing property
    host.write_text(json.dumps({}))
    res2 = generic_handler(rule, tmp_path)
    assert res2["status"] == "fail"


def test_binding_validation_pass_and_fail(tmp_path: Path) -> None:
    # valid: no function.json
    rule = _make_rule("binding_validation", {})
    res = generic_handler(rule, tmp_path)
    assert res["status"] == "pass"

    # invalid: create function.json with httpTrigger missing authLevel
    func_dir = tmp_path / "FuncA"
    func_dir.mkdir()
    func_file = func_dir / "function.json"
    func_file.write_text(json.dumps({"bindings": [{"type": "httpTrigger"}]}))
    res2 = generic_handler(rule, tmp_path)
    assert res2["status"] == "fail"


def test_cron_validation_pass_and_fail(tmp_path: Path) -> None:
    # valid cron (5 fields)
    func_dir = tmp_path / "T"
    func_dir.mkdir()
    func_file = func_dir / "function.json"
    func_file.write_text(json.dumps({"bindings": [{"type": "timerTrigger", "schedule": "0 0 * * *"}]}))
    rule = _make_rule("cron_validation", {})
    res = generic_handler(rule, tmp_path)
    assert res["status"] == "pass"

    # invalid cron
    func_file.write_text(json.dumps({"bindings": [{"type": "timerTrigger", "schedule": "everyday"}]}))
    res2 = generic_handler(rule, tmp_path)
    assert res2["status"] == "fail"
