from pathlib import Path

from azure_functions_doctor.check import run_check


def test_run_check_compare_version() -> None:
    """Test running a version comparison check."""
    rule = {
        "id": "check_python_version",
        "type": "compare_version",
        "operator": ">=",
        "value": "3.9",
        "label": "Python Version",
    }
    result = run_check(rule, Path("."))

    assert result["status"] in {"pass", "fail"}
    assert "Python Version" in result["label"]
