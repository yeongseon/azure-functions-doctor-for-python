"""Tests for improved error handling functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from azure_functions_doctor.cli import _validate_inputs
from azure_functions_doctor.doctor import Doctor
from azure_functions_doctor.handlers import _handle_specific_exceptions
from azure_functions_doctor.target_resolver import resolve_target_value


class TestSpecificExceptionHandling:
    """Test specific exception handling functionality."""

    def test_value_error_handling(self) -> None:
        result = _handle_specific_exceptions("test operation", ValueError("Invalid value"))
        assert result["status"] == "fail"
        assert "Configuration error" in result["detail"]

    def test_type_error_handling(self) -> None:
        result = _handle_specific_exceptions("test operation", TypeError("Wrong type"))
        assert result["status"] == "fail"
        assert "Configuration error" in result["detail"]

    def test_os_error_handling(self) -> None:
        result = _handle_specific_exceptions("test operation", OSError("File not found"))
        assert result["status"] == "fail"
        assert "File system error" in result["detail"]

    def test_permission_error_handling(self) -> None:
        result = _handle_specific_exceptions("test operation", PermissionError("Access denied"))
        assert result["status"] == "fail"
        assert "File system error" in result["detail"]

    def test_import_error_handling(self) -> None:
        result = _handle_specific_exceptions("test operation", ImportError("No module named 'test'"))
        assert result["status"] == "fail"
        assert "Import error" in result["detail"]

    def test_unicode_decode_error_handling(self) -> None:
        result = _handle_specific_exceptions("test operation", UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"))
        assert result["status"] == "fail"
        assert "Encoding error" in result["detail"]

    def test_memory_error_handling(self) -> None:
        result = _handle_specific_exceptions("test operation", MemoryError("Out of memory"))
        assert result["status"] == "fail"
        assert "Memory error" in result["detail"]

    def test_keyboard_interrupt_re_raise(self) -> None:
        with pytest.raises(KeyboardInterrupt):
            _handle_specific_exceptions("test operation", KeyboardInterrupt())  # type: ignore[arg-type]

    def test_system_exit_re_raise(self) -> None:
        with pytest.raises(SystemExit):
            _handle_specific_exceptions("test operation", SystemExit(1))  # type: ignore[arg-type]

    def test_unknown_exception_handling(self) -> None:
        result = _handle_specific_exceptions("test operation", RuntimeError("Unknown error"))
        assert result["status"] == "fail"
        assert "Unexpected error" in result["detail"]


class TestTargetResolverErrorHandling:
    """Test error handling in target resolver."""

    def test_func_core_tools_not_found(self) -> None:
        """Test handling when func command is not found."""
        with patch("subprocess.check_output", side_effect=FileNotFoundError()):
            result = resolve_target_value("func_core_tools")
            assert result == "not_installed"

    def test_func_core_tools_timeout(self) -> None:
        """Test handling when func command times out."""
        with patch("subprocess.check_output", side_effect=TimeoutError()):
            result = resolve_target_value("func_core_tools")
            assert result == "timeout"

    def test_func_core_tools_command_error(self) -> None:
        """Test handling when func command fails."""
        with patch("subprocess.check_output", side_effect=Exception("Command failed")):
            result = resolve_target_value("func_core_tools")
            assert result == "unknown_error"

    def test_unknown_target(self) -> None:
        """Test handling of unknown target."""
        with pytest.raises(ValueError, match="Unknown target"):
            resolve_target_value("unknown_target")


class TestCLIInputValidation:
    """Test CLI input validation error handling."""

    def test_invalid_path(self) -> None:
        """Test validation of invalid path."""
        with pytest.raises(typer.BadParameter):
            _validate_inputs("/nonexistent/path", "table", None)

    def test_path_not_directory(self) -> None:
        """Test validation when path is not a directory."""
        with tempfile.NamedTemporaryFile() as tmp_file:
            with pytest.raises(typer.BadParameter):
                _validate_inputs(tmp_file.name, "table", None)

    def test_invalid_format(self) -> None:
        """Test validation of invalid format."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(typer.BadParameter):
                _validate_inputs(tmp_dir, "invalid_format", None)

    def test_output_path_validation(self) -> None:
        """Test validation of output path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test with valid output path
            output_path = Path(tmp_dir) / "output.json"
            _validate_inputs(tmp_dir, "json", output_path)

            # Test with invalid output path (directory instead of file)
            with pytest.raises(typer.BadParameter):
                _validate_inputs(tmp_dir, "json", Path(tmp_dir))

    def test_permission_validation(self) -> None:
        """Test validation of file permissions."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Make directory read-only
            os.chmod(tmp_dir, 0o444)
            try:
                # The validation should pass because we can still read the directory
                # even with 444 permissions (owner can read)
                _validate_inputs(tmp_dir, "table", None)
            finally:
                # Restore permissions for cleanup
                os.chmod(tmp_dir, 0o755)


class TestDoctorErrorHandling:
    """Test error handling in Doctor class."""

    def test_doctor_initialization(self) -> None:
        """Test that Doctor can be initialized with a valid path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            doctor = Doctor(tmp_dir)
            assert doctor.project_path == Path(tmp_dir).resolve()

    def test_doctor_invalid_path(self) -> None:
        """Test that Doctor can be initialized with invalid path (validation happens later)."""
        # Doctor initialization doesn't validate path existence
        doctor = Doctor("/nonexistent/path")
        assert doctor.project_path == Path("/nonexistent/path").resolve()
