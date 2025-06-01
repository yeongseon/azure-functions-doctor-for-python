from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.text import Text

from azure_functions_doctor import __version__
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

        json_output = results

        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(json_output, indent=2), encoding="utf-8")
            console.print(f"[green]✓ JSON output saved to:[/green] {output}")
        else:
            print(json.dumps(json_output, indent=2))
        return

    # Print header only for table format
    console.print(f"[bold blue]🩺 Azure Functions Doctor for Python v{__version__}[/bold blue]")
    console.print(f"[bold]📁 Path:[/bold] {Path(path).resolve()}\n")

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
    console.print(summary)


# Explicit command registration (test-friendly)
cli.command()(diagnose)

if __name__ == "__main__":
    cli()
