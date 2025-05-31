import subprocess
import sys

import pytest

from azure_functions_doctor import target_resolver


def test_resolve_python_version() -> None:
    """Test resolving the current Python version."""
    result = target_resolver.resolve_target_value("python")
    assert result == sys.version.split()[0]


def test_resolve_func_core_tools_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test resolving func_core_tools version via subprocess."""

    def mock_check_output(cmd: list[str], text: bool) -> str:
        return "4.0.5198"

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)
    result = target_resolver.resolve_target_value("func_core_tools")
    assert result == "4.0.5198"


def test_resolve_func_core_tools_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test fallback when func_core_tools resolution fails."""

    def mock_check_output(cmd: list[str], text: bool) -> str:
        raise Exception("not found")

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)
    result = target_resolver.resolve_target_value("func_core_tools")
    assert result == "0.0.0"
