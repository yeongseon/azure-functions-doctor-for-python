"""Tests for rule loading functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from azure_functions_doctor.doctor import Doctor


class TestRuleLoading:
    """Test rule loading logic for different programming models."""

    def test_load_v2_rules(self) -> None:
        """Test loading rules for v2 programming model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v2 project
            python_file = temp_path / "function_app.py"
            python_file.write_text(
                """
import azure.functions as func

app = func.FunctionApp()

@app.route(route="test", auth_level=func.AuthLevel.Anonymous)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello")
"""
            )

            doctor = Doctor(str(temp_path))
            assert doctor.programming_model == "v2"

            rules = doctor.load_rules()

            # Should have common rules + v2 rules
            rule_ids = [rule["id"] for rule in rules]

            # Common rules
            assert "check_python_version" in rule_ids
            assert "check_venv" in rule_ids
            assert "check_python_executable" in rule_ids
            assert "check_requirements_txt" in rule_ids
            assert "check_host_json" in rule_ids
            assert "check_local_settings" in rule_ids

            # v2-specific rules
            assert "check_azure_functions_library" in rule_ids
            assert "check_programming_model_v2" in rule_ids

            # Should not have v1-specific rules
            assert "check_programming_model_v1" not in rule_ids

    def test_load_v1_rules(self) -> None:
        """Test loading rules for v1 programming model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v1 project
            function_json = temp_path / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

            doctor = Doctor(str(temp_path))
            assert doctor.programming_model == "v1"

            rules = doctor.load_rules()

            # Should have common rules + v1 rules
            rule_ids = [rule["id"] for rule in rules]

            # Common rules
            assert "check_python_version" in rule_ids
            assert "check_venv" in rule_ids
            assert "check_python_executable" in rule_ids
            assert "check_requirements_txt" in rule_ids
            assert "check_host_json" in rule_ids
            assert "check_local_settings" in rule_ids

            # v1-specific rules
            assert "check_programming_model_v1" in rule_ids

            # Should not have v2-specific rules
            assert "check_azure_functions_library" not in rule_ids
            assert "check_programming_model_v2" not in rule_ids

    def test_rule_loading_fallback_to_legacy(self) -> None:
        """Test that rule loading falls back to legacy rules.json when new files are missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v2 project
            python_file = temp_path / "function_app.py"
            python_file.write_text(
                """
import azure.functions as func

app = func.FunctionApp()

@app.route(route="test", auth_level=func.AuthLevel.Anonymous)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello")
"""
            )

            doctor = Doctor(str(temp_path))

            # Mock the new rule files to not exist; expect explicit v2.json error
            with patch("importlib.resources.files") as mock_files:
                mock_files.return_value.joinpath.return_value.open.side_effect = FileNotFoundError()

                with pytest.raises(RuntimeError, match="v2.json not found"):
                    doctor.load_rules()

    def test_rule_loading_handles_json_errors(self) -> None:
        """Test that rule loading handles JSON parsing errors gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v2 project
            python_file = temp_path / "function_app.py"
            python_file.write_text(
                """
import azure.functions as func

app = func.FunctionApp()

@app.route(route="test", auth_level=func.AuthLevel.Anonymous)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello")
"""
            )

            doctor = Doctor(str(temp_path))

            # Mock v2.json to have invalid JSON
            with patch("importlib.resources.files") as mock_files:
                mock_v2_path = mock_files.return_value.joinpath.return_value
                mock_v2_path.open.return_value.__enter__.return_value.read.return_value = "invalid json"

                with pytest.raises(RuntimeError, match="Failed to parse v2.json"):
                    doctor.load_rules()

    def test_rule_loading_handles_missing_v2_rules(self) -> None:
        """Test that rule loading handles missing v2.json gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v2 project
            python_file = temp_path / "function_app.py"
            python_file.write_text(
                """
import azure.functions as func

app = func.FunctionApp()

@app.route(route="test", auth_level=func.AuthLevel.Anonymous)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello")
"""
            )

            doctor = Doctor(str(temp_path))

            # Mock v2.json to not exist
            with patch("importlib.resources.files") as mock_files:
                # Mock common.json exists
                mock_common_path = mock_files.return_value.joinpath.return_value
                mock_common_path.open.return_value.__enter__.return_value.read.return_value = json.dumps(
                    [{"id": "common_rule", "check_order": 1}]
                )

                # Mock v2.json not found
                mock_v2_path = mock_files.return_value.joinpath.return_value
                mock_v2_path.open.side_effect = FileNotFoundError()

                # With common.json handling removed, expect an explicit error
                with pytest.raises(RuntimeError, match="v2.json not found"):
                    doctor.load_rules()

    def test_rule_loading_handles_missing_v1_rules(self) -> None:
        """Test that rule loading handles missing v1.json gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v1 project
            function_json = temp_path / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

            doctor = Doctor(str(temp_path))

            # Mock v1.json to not exist
            with patch("importlib.resources.files") as mock_files:
                # Mock common.json exists
                mock_common_path = mock_files.return_value.joinpath.return_value
                mock_common_path.open.return_value.__enter__.return_value.read.return_value = json.dumps(
                    [{"id": "common_rule", "check_order": 1}]
                )

                # Mock v1.json not found
                mock_v1_path = mock_files.return_value.joinpath.return_value
                mock_v1_path.open.side_effect = FileNotFoundError()

                # With common.json handling removed, expect an explicit error
                with pytest.raises(RuntimeError, match="v1.json not found"):
                    doctor.load_rules()

    def test_rule_ordering(self) -> None:
        """Test that rules are properly ordered by check_order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v2 project
            python_file = temp_path / "function_app.py"
            python_file.write_text(
                """
import azure.functions as func

app = func.FunctionApp()

@app.route(route="test", auth_level=func.AuthLevel.Anonymous)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello")
"""
            )

            doctor = Doctor(str(temp_path))
            rules = doctor.load_rules()

            # Check that rules are sorted by check_order
            check_orders = [rule.get("check_order", 999) for rule in rules]
            assert check_orders == sorted(check_orders)

    def test_rule_loading_with_no_rules_files(self) -> None:
        """Test that rule loading fails gracefully when no rules files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v2 project
            python_file = temp_path / "function_app.py"
            python_file.write_text(
                """
import azure.functions as func

app = func.FunctionApp()

@app.route(route="test", auth_level=func.AuthLevel.Anonymous)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello")
"""
            )

            doctor = Doctor(str(temp_path))

            # Mock all rule files to not exist
            with patch("importlib.resources.files") as mock_files:
                mock_files.return_value.joinpath.return_value.open.side_effect = FileNotFoundError()

                # Now loader only looks for v2.json (project is v2), so expect that error
                with pytest.raises(RuntimeError, match="v2.json not found"):
                    doctor.load_rules()
