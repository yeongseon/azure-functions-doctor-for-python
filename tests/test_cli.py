from typer.testing import CliRunner

from azure_functions_doctor.cli import app

runner = CliRunner()


def test_main_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Azure Functions Doctor CLI Tool" in result.output


def test_main_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "azure-functions-doctor" in result.output
