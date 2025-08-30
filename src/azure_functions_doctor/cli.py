import json
import time
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.text import Text

from azure_functions_doctor import __version__
from azure_functions_doctor.doctor import Doctor
from azure_functions_doctor.logging_config import (
    get_logger,
    log_diagnostic_complete,
    log_diagnostic_start,
    setup_logging,
)
from azure_functions_doctor.utils import format_detail, format_result, format_status_icon

cli = typer.Typer()
console = Console()
logger = get_logger(__name__)


def _validate_inputs(path: str, format_type: str, output: Optional[Path]) -> None:
    """Validate CLI inputs before processing."""
    path_obj = Path(path)
    if not path_obj.exists():
        raise typer.BadParameter(f"Path does not exist: {path}")

    if not path_obj.is_dir():
        raise typer.BadParameter(f"Path must be a directory: {path}")

    if format_type not in ["table", "json"]:
        raise typer.BadParameter(f"Invalid format: {format_type}. Must be 'table' or 'json'")

    if output:
        if output.exists() and not output.is_file():
            raise typer.BadParameter(f"Output path exists but is not a file: {output}")

        # Check if parent directory exists or can be created
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise typer.BadParameter(f"Cannot create output directory: {e}") from e


@cli.command()
def diagnose(
    path: str = ".",
    verbose: bool = False,
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
    elif verbose:
        setup_logging(level="INFO", format_style="simple")
    else:
        # Use environment variable or default to WARNING
        setup_logging(level=None, format_style="simple")

    start_time = time.time()
    doctor = Doctor(path)
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

    passed = failed = 0

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

    # Print header only for table format
    console.print(f"[bold blue]🩺 Azure Functions Doctor for Python v{__version__}[/bold blue]")
    console.print(f"[bold]📁 Path:[/bold] {resolved_path}\n")

    if debug:
        console.print("[dim]Debug logging enabled - check stderr for detailed logs[/dim]\n")

    # Default: table format
    for section in results:
        console.print(Text.assemble("\n", format_result(section["status"]), " ", (section["title"], "bold")))

        if section["status"] == "pass":
            passed += 1
        else:
            failed += 1

        for item in section["items"]:
            label = item["label"]
            value = item["value"]
            status = item["status"]

            line = Text.assemble(
                ("  • ", "default"),
                (label, "dim"),
                (": ", "default"),
                format_detail(status, value),
            )
            console.print(line)

            if verbose and status != "pass":
                if item.get("hint"):
                    console.print(f"    ↪ [yellow]{item['hint']}[/yellow]")
                hint_url = item.get("hint_url", "")
                if hint_url.strip():
                    console.print(f"    📚 [blue]{hint_url}[/blue]")

    # ✅ Summary section
    console.print()
    console.print("[bold]Summary[/bold]")
    summary = Text.assemble(
        (f"{format_status_icon('pass')} ", "green bold"),
        (f"{passed} Passed    ", "bold"),
        (f"{format_status_icon('fail')} ", "red bold"),
        (f"{failed} Failed", "bold"),
    )

    if errors > 0:
        summary = Text.assemble(
            summary,
            ("    ⚠ ", "yellow bold"),
            (f"{errors} Errors", "bold"),
        )

    if debug:
        summary = Text.assemble(
            summary,
            ("    🕒 ", "dim"),
            (f"{duration_ms:.1f}ms", "dim"),
        )

    console.print(summary)


# Explicit command registration (test-friendly)
cli.command()(diagnose)

if __name__ == "__main__":
    cli()
