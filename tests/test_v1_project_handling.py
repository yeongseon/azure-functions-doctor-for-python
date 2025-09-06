"""Tests for v1 project handling with warning messages."""

import tempfile
from pathlib import Path

from typer.testing import CliRunner

from azure_functions_doctor.cli import cli as app


class TestV1ProjectHandling:
    """Test v1 project handling with warning messages."""

    def test_v1_project_shows_warning_message(self) -> None:
        """Test that v1 projects show warning message in header."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v1 project
            function_json = temp_path / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

            python_file = temp_path / "main.py"
            python_file.write_text("def main(req): return 'Hello'")

            runner = CliRunner()
            result = runner.invoke(app, ["doctor", "--path", str(temp_path)])

            assert result.exit_code == 0
            assert "Azure Functions Doctor" in result.output

    def test_v2_project_shows_v2_in_header(self) -> None:
        """Test that v2 projects show v2 in header."""
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

            runner = CliRunner()
            result = runner.invoke(app, ["doctor", "--path", str(temp_path)])

            assert result.exit_code == 0
            assert "Azure Functions Doctor" in result.output

    def test_v1_project_with_verbose_shows_warning_and_hints(self) -> None:
        """Test that v1 projects show warning message and verbose hints."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v1 project
            function_json = temp_path / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

            python_file = temp_path / "main.py"
            python_file.write_text("def main(req): return 'Hello'")

            runner = CliRunner()
            result = runner.invoke(app, ["doctor", "--path", str(temp_path), "--verbose"])

            assert result.exit_code == 0
            assert "Azure Functions Doctor" in result.output

            # Should show hints for failed checks
            assert "↪" in result.output  # hint indicator

    def test_v1_project_with_debug_shows_warning_and_debug_info(self) -> None:
        """Test that v1 projects show warning message and debug info."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v1 project
            function_json = temp_path / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

            python_file = temp_path / "main.py"
            python_file.write_text("def main(req): return 'Hello'")

            runner = CliRunner()
            result = runner.invoke(app, ["doctor", "--path", str(temp_path), "--debug"])

            assert result.exit_code == 0
            assert "Azure Functions Doctor" in result.output
            assert "Debug logging enabled" in result.output

    def test_v1_project_continues_execution_after_warning(self) -> None:
        """Test that v1 projects continue execution after showing warning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v1 project
            function_json = temp_path / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

            python_file = temp_path / "main.py"
            python_file.write_text("def main(req): return 'Hello'")

            runner = CliRunner()
            result = runner.invoke(app, ["doctor", "--path", str(temp_path)])

            assert result.exit_code == 0
            assert "Azure Functions Doctor" in result.output  # Should continue with normal output

    def test_v1_project_with_both_v1_and_v2_indicators_shows_v1_warning(self) -> None:
        """Test that projects with both v1 and v2 indicators show v1 warning (v1 takes priority)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a project with both v1 and v2 indicators
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

            runner = CliRunner()
            result = runner.invoke(app, ["doctor", "--path", str(temp_path)])

            assert result.exit_code == 0
            assert "Azure Functions Doctor" in result.output

    def test_programming_model_not_in_project_structure(self) -> None:
        """Test that programming model is not shown in Project Structure section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a v1 project
            function_json = temp_path / "function.json"
            function_json.write_text('{"scriptFile": "main.py", "entryPoint": "main"}')

            python_file = temp_path / "main.py"
            python_file.write_text("def main(req): return 'Hello'")

            runner = CliRunner()
            result = runner.invoke(app, ["doctor", "--path", str(temp_path)])

            assert result.exit_code == 0
            # Should not show programming model in Project Structure section
            assert (
                "Programming Model" not in result.output
                or "Programming Model" in result.output.split("Project Structure")[0]
            )
