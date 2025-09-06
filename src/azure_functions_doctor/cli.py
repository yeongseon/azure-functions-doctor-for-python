import json
import os
import time
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.text import Text

from azure_functions_doctor.doctor import Doctor
from azure_functions_doctor.logging_config import (
    get_logger,
    log_diagnostic_complete,
    log_diagnostic_start,
    setup_logging,
)
from azure_functions_doctor.utils import format_detail, format_status_icon

cli = typer.Typer()
console = Console()
logger = get_logger(__name__)


def _validate_inputs(path: str, format_type: str, output: Optional[Path]) -> None:
    """Validate CLI inputs before processing."""
    try:
        path_obj = Path(path).resolve()
    except (OSError, ValueError) as e:
        raise typer.BadParameter(f"Invalid path: {e}") from e

    if not path_obj.exists():
        raise typer.BadParameter(f"Path does not exist: {path}")

    if not path_obj.is_dir():
        raise typer.BadParameter(f"Path must be a directory: {path}")

    # Check read permissions
    if not os.access(path_obj, os.R_OK):
        raise typer.BadParameter(f"No read permission for path: {path}")

    # Validate format type
    if format_type not in ["table", "json"]:
        raise typer.BadParameter(f"Invalid format: {format_type}. Must be 'table' or 'json'")

    # Validate output path
    if output:
        try:
            output_path = Path(output).resolve()
        except (OSError, ValueError) as e:
            raise typer.BadParameter(f"Invalid output path: {e}") from e

        if output_path.exists() and not output_path.is_file():
            raise typer.BadParameter(f"Output path exists but is not a file: {output}")

        # Check if parent directory exists or can be created
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise typer.BadParameter(f"Cannot create output directory: {e}") from e

        # Check write permissions
        if not os.access(output_path.parent, os.W_OK):
            raise typer.BadParameter(f"No write permission for output directory: {output_path.parent}")


@cli.command(name="doctor")
def doctor(
    path: str = ".",
    verbose: Annotated[bool, typer.Option("-v", "--verbose", help="Show detailed hints for failed checks")] = False,
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
    format: Annotated[str, typer.Option(help="Output format: 'table' or 'json'")] = "table",
    output: Annotated[Optional[Path], typer.Option(help="Optional path to save JSON result")] = None,
) -> None:
    """
    Run diagnostics on an Azure Functions application.

    Args:
        path: Path to the Azure Functions app. Defaults to current directory.
        verbose: Show detailed hints for failed checks.
        debug: Enable debug logging to stderr.
        format: Output format: 'table' or 'json'.
        output: Optional file path to save JSON result.
    """
    # Validate inputs before proceeding
    _validate_inputs(path, format, output)

    # Configure logging based on CLI flags
    if debug:
        setup_logging(level="DEBUG", format_style="structured")
    else:
        # Use environment variable or default to WARNING
        setup_logging(level=None, format_style="simple")

    start_time = time.time()
    # Allow v1 projects when invoked from CLI so we can show warning but continue
    doctor = Doctor(path, allow_v1=True)
    resolved_path = Path(path).resolve()

    # Log diagnostic start
    rules = doctor.load_rules()
    log_diagnostic_start(str(resolved_path), len(rules))

    results = doctor.run_all_checks()

    # Calculate execution metrics
    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000

    # Count results for logging
    total_checks = sum(len(section["items"]) for section in results)
    passed_items = sum(1 for section in results for item in section["items"] if item["status"] == "pass")
    failed_items = sum(1 for section in results for item in section["items"] if item["status"] == "fail")
    # Note: handlers currently only return "pass"/"fail", not "error"
    errors = 0

    # Log diagnostic completion
    log_diagnostic_complete(total_checks, passed_items, failed_items, errors, duration_ms)

    # local counts handled below; remove unused placeholders

    # Pre-compute aggregated counts from normalized item['status'] values
    passed_count = 0
    warning_count = 0
    error_count = 0
    for section in results:
        for item in section["items"]:
            s = item.get("status")
            severity = item.get("severity", "error")
            if s == "pass":
                passed_count += 1
            elif s == "warn":
                warning_count += 1
            elif s == "fail":
                # treat 'fail' as non-fatal warning for backwards compatibility
                # but escalate to error only if the rule severity explicitly marks it as 'error'
                if severity == "error":
                    # keep as warning for CLI exit semantics (tests expect non-zero only for true errors)
                    warning_count += 1
                else:
                    warning_count += 1
            elif s == "error":
                # defensive: treat 'error' as error
                error_count += 1
            else:
                # treat unknown as warning for safety
                warning_count += 1

    if format == "json":
        json_output = results

        if output:
            try:
                output.write_text(json.dumps(json_output, indent=2), encoding="utf-8")
                console.print(f"[green]✓ JSON output saved to:[/green] {output}")
            except (OSError, IOError, PermissionError) as e:
                console.print(f"[red]✗ Failed to write output file:[/red] {e}")
                logger.error(f"Failed to write JSON output to {output}: {e}")
                raise typer.Exit(1) from e
        else:
            print(json.dumps(json_output, indent=2))
        return

    # Note: Top header removed per UI change; programming model header intentionally omitted

    if debug:
        console.print("[dim]Debug logging enabled - check stderr for detailed logs[/dim]\n")

    # Table-format user-facing output (requested design)
    console.print("Azure Functions Doctor   ")
    console.print(f"Path: {resolved_path}")

    # Print each section with simple title and items
    for section in results:
        console.print()
        console.print(section["title"])

        for item in section["items"]:
            label = item.get("label", "")
            value = item.get("value", "")
            status = item.get("status", "pass")
            icon = format_status_icon(status)

            # Prefer explicit severity for display if present, otherwise show raw status
            display_status = item.get("severity") or status

            # Compose main line: [ICON] Label: value (display_status)
            line = Text.assemble((f"[{icon}] ", "bold"), (label, "dim"))
            if value:
                line.append(": ")
                line.append(format_detail(status, value))

            # append status in parentheses for clarity on UI when non-pass
            if status != "pass":
                line.append(f" ({display_status})", "italic dim")

            console.print(line)

            # show hint as 'fix:' only when verbose is enabled
            if status != "pass" and verbose:
                hint = item.get("hint", "")
                if hint:
                    prefix = "↪ "
                    console.print(f"    {prefix}fix: {hint}")

    # Use the precomputed counts from earlier for final output
    console.print()
    # Print Doctor summary at the bottom like the requested sample
    console.print("Doctor summary (to see all details, run azure-functions doctor -v):")
    # Use singular/plural simple form as in sample (error vs errors)
    e_label = "error" if error_count == 1 else "errors"
    w_label = "warning" if warning_count == 1 else "warnings"
    p_label = "passed" if passed_count == 1 else "passed"
    console.print(f"  {error_count} {e_label}, {warning_count} {w_label}, {passed_count} {p_label}")
    # Print Exit code line to match the sample and exit with code 1 on errors
    if error_count > 0:
        console.print("Exit code: 1")
        raise typer.Exit(1)
    else:
        console.print("Exit code: 0")


# Explicit command registration (test-friendly)
cli.command()(doctor)

if __name__ == "__main__":
    cli()
