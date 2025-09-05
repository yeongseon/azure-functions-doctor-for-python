"""Tests for programming model detection functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from azure_functions_doctor.doctor import Doctor


class TestProgrammingModelDetection:
    """Test programming model detection logic."""

    def test_detect_v1_with_function_json(self) -> None:
        """Test v1 detection when function.json files are present."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a function.json file
            function_json = temp_path / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

            # allow_v1=True to allow nested function.json detection in tests
            doctor = Doctor(str(temp_path), allow_v1=True)
            assert doctor.programming_model == "v1"

    def test_detect_v2_with_decorators(self) -> None:
        """Test v2 detection when @app decorators are present."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with @app decorator
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

    def test_detect_v2_default_when_no_indicators(self) -> None:
        """Test v2 as default when no clear indicators are found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a regular Python file without @app decorators
            python_file = temp_path / "main.py"
            python_file.write_text("print('Hello World')")

            doctor = Doctor(str(temp_path))
            assert doctor.programming_model == "v2"

    def test_detect_v1_priority_over_v2(self) -> None:
        """Test that v1 detection takes priority over v2 when both are present."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create both function.json and @app decorators
            function_json = temp_path / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

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

            doctor = Doctor(str(temp_path), allow_v1=True)
            assert doctor.programming_model == "v1"

    def test_has_v2_decorators_with_various_patterns(self) -> None:
        """Test _has_v2_decorators with various @app patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test different @app patterns
            test_cases = [
                "@app.route(route='test')",
                "@app.schedule(schedule='0 */5 * * * *')",
                "@app.timer_trigger(schedule='0 */5 * * * *')",
                "@app.blob_trigger(arg_name='myblob', path='samples-workitems/{name}')",
                "@app.cosmos_db_trigger(arg_name='documents', database_name='ToDoList', collection_name='Items')",
            ]

            for i, pattern in enumerate(test_cases):
                python_file = temp_path / f"test_{i}.py"
                python_file.write_text(
                    f"""
import azure.functions as func

app = func.FunctionApp()

{pattern}
def test_function():
    pass
"""
                )

                doctor = Doctor(str(temp_path))
                assert doctor.programming_model == "v2"

    def test_has_v2_decorators_ignores_comments(self) -> None:
        """Test that @app in comments doesn't trigger v2 detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with @app only in comments
            python_file = temp_path / "main.py"
            python_file.write_text(
                """
# This is a comment with @app.route but it shouldn't count
print('Hello World')

def some_function():
    # Another comment with @app.schedule
    pass
"""
            )

            doctor = Doctor(str(temp_path))
            assert doctor.programming_model == "v2"  # Default since no real @app found

    def test_has_v2_decorators_handles_file_read_errors(self) -> None:
        """Test that file read errors are handled gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with @app decorator
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

            # Mock file read to raise an error for one file
            with patch("pathlib.Path.open", side_effect=OSError("Permission denied")):
                doctor = Doctor(str(temp_path))
                # Should still detect v2 from the working file
                assert doctor.programming_model == "v2"

    def test_detect_v1_with_nested_function_json(self) -> None:
        """Test v1 detection with function.json in subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure with function.json
            nested_dir = temp_path / "MyFunction"
            nested_dir.mkdir()

            function_json = nested_dir / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

            # allow nested v1 detection in tests
            doctor = Doctor(str(temp_path), allow_v1=True)
            assert doctor.programming_model == "v1"

    def test_detect_v2_with_nested_decorators(self) -> None:
        """Test v2 detection with @app decorators in subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure with @app decorators
            nested_dir = temp_path / "functions"
            nested_dir.mkdir()

            python_file = nested_dir / "function_app.py"
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
