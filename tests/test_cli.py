import json
import re

from typer.testing import CliRunner

from azure_functions_doctor.cli import cli as app

runner = CliRunner()


def _assert_exit_code_matches_fail_count_text(output: str, exit_code: int) -> None:
    """Parse fail count from human table output summary and validate exit code.

    Summary line format: '  <fail_count> fail(s), <warning_count> warning(s), <passed_count> passed'
    We extract the first '<number> fail' occurrence.
    """
    match = re.search(r"(^|\n)\s*(\d+)\s+fail", output)
    if match:
        fail_count = int(match.group(2))
        expected = 1 if fail_count > 0 else 0
        assert (
            exit_code == expected
        ), f"Expected exit {expected} for {fail_count} fails, got {exit_code}. Output:\n{output}"
    else:
        # If no summary found, keep original expectation of success
        assert exit_code == 0, f"No fail summary found. Output:\n{output}"


def test_cli_table_output() -> None:
    """Test CLI outputs result in table format."""
    result = runner.invoke(app, ["doctor", "--format", "table"])
    _assert_exit_code_matches_fail_count_text(result.output, result.exit_code)
    assert "Azure Functions Doctor" in result.output
    assert any(icon in result.output for icon in ["✓", "✗", "!"])


def test_cli_json_output() -> None:
    """Test CLI outputs result in JSON format without extra text and exit code matches fail count."""
    result = runner.invoke(app, ["doctor", "--format", "json"])
    output_text = result.output.strip()
    try:
        data = json.loads(output_text)
    except json.JSONDecodeError as err:
        raise AssertionError("Output is not valid JSON") from err
    assert isinstance(data, list)
    assert all("title" in section and "items" in section for section in data)
    # Derive fail count from JSON structure
    fail_count = sum(1 for section in data for item in section.get("items", []) if item.get("status") == "fail")
    expected_exit = 1 if fail_count > 0 else 0
    assert (
        result.exit_code == expected_exit
    ), f"Expected exit {expected_exit} with {fail_count} fails, got {result.exit_code}. JSON: {output_text[:500]}"


def test_cli_verbose_output() -> None:
    """Test CLI outputs verbose hints when enabled."""
    result = runner.invoke(app, ["doctor", "--format", "table", "--verbose"])
    _assert_exit_code_matches_fail_count_text(result.output, result.exit_code)
    assert "fix:" in result.output  # hint indicator now printed as 'fix:'
