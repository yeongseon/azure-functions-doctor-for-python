from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.text import Text

from azure_functions_doctor.doctor import Doctor
from azure_functions_doctor.utils import format_detail, format_result, format_status_icon

cli = typer.Typer()
console = Console()


@cli.command()
def diagnose(
    path: str = ".",
    verbose: bool = False,
    format: Annotated[str, typer.Option(help="Output format: 'table' or 'json'")] = "table",
    output: Annotated[Optional[Path], typer.Option(help="Optional path to save JSON result")] = None,
) -> None:
    """
    Run diagnostics on an Azure Functions application.

    Args:
        path: Path to the Azure Functions app. Defaults to current directory.
        verbose: Show detailed hints for failed checks.
        format: Output format: 'table' or 'json'.
        output: Optional file path to save JSON result.
    """
    doctor = Doctor(path)
    results = doctor.run_all_checks()

    passed = failed = 0

    if format == "json":
        import json

        json_output = results  # Already a list of dictionaries
        console.print_json(data=json_output)

        if output:
            output.write_text(json.dumps(json_output, indent=2))
            console.print(f"[green]✓ JSON output written to:[/green] {output}")
        return

    # Default: table format
    for section in results:
        # Section header with icon and bold title
        console.print(Text.assemble("\n", format_result(section["status"]), " ", (section["title"], "bold")))

        if section["status"] == "pass":
            passed += 1
        else:
            failed += 1

        for item in section["items"]:
            status = item["status"]
            label = item["label"]
            value = item["value"]

            line = Text.assemble(("  • ", "default"), (label, "dim"), (": ", "default"), format_detail(status, value))
            console.print(line)

            if verbose and status != "pass":
                if item.get("hint"):
                    console.print(f"    ↪ {item['hint']}")
                if item.get("doc"):
                    console.print(f"    📚 {item['doc']}")

    # Summary section
    console.print()
    console.rule("[bold]Summary")
    summary = Text.assemble(
        (f"{format_status_icon('pass')} ", "green"),
        f"{passed} Passed    ",
        (f"{format_status_icon('fail')} ", "red"),
        f"{failed} Failed",
    )
    console.print(summary)


# Explicit command registration (optional but test-friendly)
cli.command()(diagnose)

if __name__ == "__main__":
    cli()
