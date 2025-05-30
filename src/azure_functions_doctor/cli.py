import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from azure_functions_doctor.doctor import Doctor

cli = typer.Typer()
console = Console()


@cli.command("diagnose")
def diagnose(
    path: str = ".", verbose: bool = False, format: str = typer.Option("table", help="Output format: table or json")
) -> None:
    """Run diagnostics on an Azure Functions application.
    Parameters:
        path: The file system path to the Azure Functions application. Defaults to the current directory.
        verbose: If true, display detailed recommendations and documentation links for failed checks.
        format: The output format for the results. Can be 'table' or 'json'. Defaults to 'table'.
    Returns:
        None: This function prints the diagnostic results to the console.
    Raises:
        typer.Exit: If an error occurs during diagnostics, this will exit the CLI with an error code.
    """
    doctor = Doctor(path)
    results = doctor.run_all_checks()

    if format == "json":
        console.print_json(data=[r.__dict__ for r in results])
        return

    table = Table(title="Azure Function Diagnostics", box=box.SIMPLE_HEAD)
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Result", style="bold")
    table.add_column("Detail")

    status_icons = {
        "pass": "✅",
        "fail": "❌",
        "warn": "⚠️",
    }

    for r in results:
        icon = status_icons.get(r.result, "❓")
        result_text = f"{icon} {r.result.upper()}"
        table.add_row(r.check, result_text, r.detail)

    console.print(table)

    if verbose:
        for r in results:
            if r.result != "pass":
                console.print(
                    Panel(
                        f"[bold]{r.check}[/bold]\n\n"
                        f"[yellow]Recommendation:[/yellow] {r.recommendation}\n"
                        f"[blue]Docs:[/blue] {r.docs_url}",
                        title=f"ℹ️ Details: {r.check}",
                        expand=False,
                    )
                )


# Explicitly register the command for CLI and testing purposes
cli.command()(diagnose)

if __name__ == "__main__":
    cli()
