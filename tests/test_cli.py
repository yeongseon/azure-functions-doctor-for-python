from click.testing import CliRunner

from azure_functions_doctor.cli import cli

runner = CliRunner()


def test_main_help() -> None:
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_main_version() -> None:
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "azure-functions-doctor" in result.output
