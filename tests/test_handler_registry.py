"""Tests for the handler registry pattern."""

import sys
import tempfile
from pathlib import Path
from typing import cast

from azure_functions_doctor.handlers import HandlerRegistry, Rule


def test_handler_registry_initialization() -> None:
    """Test that handler registry initializes with all expected handlers."""
    registry = HandlerRegistry()

    expected_handlers = [
        "compare_version",
        "env_var_exists",
        "path_exists",
        "file_exists",
        "package_installed",
        "source_code_contains",
    ]

    for handler_type in expected_handlers:
        assert handler_type in registry._handlers


def test_handler_registry_unknown_type() -> None:
    """Test registry handling of unknown check types."""
    registry = HandlerRegistry()

    # Create rule with intentionally invalid type for testing error handling
    rule = cast(
        Rule,
        {
            "id": "test_unknown",
            "type": "unknown_type_xyz",
        },
    )

    result = registry.handle(rule, Path("."))

    assert result["status"] == "fail"
    assert "Unknown check type" in result["detail"]


def test_handler_registry_compare_version() -> None:
    """Test version comparison through registry."""
    registry = HandlerRegistry()

    rule: Rule = {
        "id": "test_python_version",
        "type": "compare_version",
        "condition": {
            "target": "python",
            "operator": ">=",
            "value": f"{sys.version_info.major}.{sys.version_info.minor}",
        },
    }

    result = registry.handle(rule, Path("."))

    assert result["status"] == "pass"
    assert "Python version is" in result["detail"]


def test_handler_registry_env_var_exists() -> None:
    """Test environment variable check through registry."""
    registry = HandlerRegistry()

    rule: Rule = {
        "id": "test_env_var",
        "type": "env_var_exists",
        "condition": {
            "target": "PATH",  # Should exist on all systems
        },
    }

    result = registry.handle(rule, Path("."))

    assert result["status"] == "pass"
    assert "PATH is set" in result["detail"]


def test_handler_registry_path_exists() -> None:
    """Test path existence check through registry."""
    registry = HandlerRegistry()

    rule: Rule = {
        "id": "test_path_exists",
        "type": "path_exists",
        "condition": {
            "target": "sys.executable",
        },
    }

    result = registry.handle(rule, Path("."))

    assert result["status"] == "pass"
    assert "exists" in result["detail"]


def test_handler_registry_file_exists() -> None:
    """Test file existence check through registry."""
    registry = HandlerRegistry()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test content")
        tmp_path = Path(tmp.name)

    try:
        rule: Rule = {
            "id": "test_file_exists",
            "type": "file_exists",
            "condition": {
                "target": tmp_path.name,
            },
        }

        result = registry.handle(rule, tmp_path.parent)

        assert result["status"] == "pass"
        assert "exists" in result["detail"]

    finally:
        tmp_path.unlink()


def test_handler_registry_package_installed() -> None:
    """Test package installation check through registry."""
    registry = HandlerRegistry()

    # Test with a standard library module that should always exist
    rule: Rule = {
        "id": "test_package_installed",
        "type": "package_installed",
        "condition": {
            "target": "os",
        },
    }

    result = registry.handle(rule, Path("."))

    assert result["status"] == "pass"
    assert "is installed" in result["detail"]


def test_handler_registry_source_code_contains() -> None:
    """Test source code search through registry."""
    registry = HandlerRegistry()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a Python file with specific content
        py_file = tmp_path / "test_file.py"
        py_file.write_text("# Test keyword found here")

        rule: Rule = {
            "id": "test_source_code_contains",
            "type": "source_code_contains",
            "condition": {
                "keyword": "Test keyword",
            },
        }

        result = registry.handle(rule, tmp_path)

        assert result["status"] == "pass"
        assert "found" in result["detail"]


def test_handler_registry_exception_handling() -> None:
    """Test registry exception handling."""
    registry = HandlerRegistry()

    # Create a rule that will cause an exception (missing condition)
    rule: Rule = {
        "id": "test_exception",
        "type": "compare_version",
        "condition": {},  # Missing required fields
    }

    result = registry.handle(rule, Path("."))

    # Should handle the exception gracefully
    assert result["status"] == "fail"
    assert "Missing condition fields" in result["detail"]


def test_handler_registry_optional_rules() -> None:
    """Test registry handling of optional rules."""
    registry = HandlerRegistry()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        rule: Rule = {
            "id": "test_optional_file",
            "type": "file_exists",
            "required": False,
            "condition": {
                "target": "nonexistent_file.txt",
            },
        }

        result = registry.handle(rule, tmp_path)

        assert result["status"] == "pass"
        assert "optional" in result["detail"]
