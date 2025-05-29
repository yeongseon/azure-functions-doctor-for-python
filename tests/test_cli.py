import json
import os
import tempfile

from typer.testing import CliRunner

from azure_functions_doctor.cli import cli

runner = CliRunner()


def test_cli_text_output() -> None:
    """Test the CLI output in text format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "host.json"), "w") as f:
            json.dump({"version": "2.0"}, f)
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("azure-functions\n")

        result = runner.invoke(cli, ["diagnose", "--path", tmpdir])
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("EXCEPTION:", result.exception)
        assert result.exit_code == 0
        assert "host.json version" in result.stdout


def test_cli_json_output() -> None:
    """Test the CLI output in JSON format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "host.json"), "w") as f:
            json.dump({"version": "2.0"}, f)
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("azure-functions\n")

        result = runner.invoke(cli, ["diagnose", "--path", tmpdir, "--json-output"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert isinstance(output, list)
        assert any(r["check"] == "host.json version" for r in output)
