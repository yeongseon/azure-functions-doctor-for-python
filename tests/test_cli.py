import json
import subprocess
import sys
from subprocess import CompletedProcess


def run_cli_command(*args: str) -> CompletedProcess[str]:
    """Run the Azure Functions Doctor CLI command with the given arguments."""
    result = subprocess.run(
        [sys.executable, "-m", "azure_functions_doctor.cli", *args],
        capture_output=True,
        text=True,
    )
    return result


def test_run_cli_table_output() -> None:
    """Checks that the CLI runs and outputs results in table format."""
    result = run_cli_command("diagnose", "--format", "table")
    assert result.returncode == 0
    assert "Azure Function Diagnostics" in result.stdout
    assert any(s in result.stdout for s in ["✅", "❌", "⚠️"])


def test_run_cli_json_output() -> None:
    """Checks that the CLI runs and outputs results in JSON format."""
    result = run_cli_command("diagnose", "--format", "json")
    assert result.returncode == 0
    try:
        output = json.loads(result.stdout)
        assert isinstance(output, list)
        assert all("check" in r and "result" in r for r in output)
    except json.JSONDecodeError as err:
        raise AssertionError("Output is not valid JSON") from err


def test_run_cli_verbose_output() -> None:
    """Checks that the CLI runs and outputs verbose details for failed checks."""
    result = run_cli_command("diagnose", "--verbose")
    assert result.returncode == 0
    assert "Recommendation:" in result.stdout or "Docs:" in result.stdout
