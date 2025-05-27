"""CLI entry point for Azure Functions Doctor.

Defines the Typer CLI application and commands for running diagnostics and showing the version.
"""
import typer

from azure_functions_doctor.doctor import run_diagnostics

from . import __version__

app = typer.Typer(add_completion=False)


@app.callback()
def cli(
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
) -> None:
    """Main CLI callback for Azure Functions Doctor.

    Handles the --version option and exits if specified.
    """
    if version:
        typer.echo(f"azure-functions-doctor v{__version__}")
        raise typer.Exit()


@app.command()
def run() -> None:
    """Run the Azure Function diagnostics."""
    run_diagnostics()


def main() -> None:
    """Entrypoint for the CLI application."""
    app()
