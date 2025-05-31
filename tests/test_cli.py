import json

from typer.testing import CliRunner

from azure_functions_doctor.cli import cli as app

runner = CliRunner()


def test_cli_table_output() -> None:
    """Test CLI outputs result in table format."""
    result = runner.invoke(app, ["diagnose", "--format", "table"])
    assert result.exit_code == 0
    assert any(icon in result.output for icon in ["✔", "✖", "⚠"])


def test_cli_json_output() -> None:
    """Test CLI outputs result in JSON format."""
    result = runner.invoke(app, ["diagnose", "--format", "json"])
    assert result.exit_code == 0
    try:
        output = json.loads(result.output)
        assert isinstance(output, list)
        assert all("title" in section and "items" in section for section in output)
    except json.JSONDecodeError as err:
        raise AssertionError("Output is not valid JSON") from err


def test_cli_verbose_output() -> None:
    """Test CLI outputs verbose hints when enabled."""
    result = runner.invoke(app, ["diagnose", "--verbose"])
    assert result.exit_code == 0
    assert "↪" in result.output  # hint indicator
