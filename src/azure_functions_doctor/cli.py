"""
CLI entry point for Azure Functions Doctor.

Defines the Typer CLI application and commands for running diagnostics and showing the version.
"""

import typer

from azure_functions_doctor import __version__
from azure_functions_doctor.doctor import run_diagnostics

app = typer.Typer(help="Azure Functions Doctor CLI Tool")


@app.command("run", help="Run the Azure Function diagnostics.")
def run_command() -> None:
    """Run diagnostics logic."""
    run_diagnostics()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        is_eager=True,
        help="Show the version and exit.",
        callback=lambda value: _handle_version_option(value),
    )
) -> None:
    """Azure Functions Doctor CLI Tool"""
    pass


def _handle_version_option(value: bool) -> None:
    """Handle --version option."""
    if value:
        print(f"azure-functions-doctor v{__version__}")
        raise typer.Exit()


def main() -> None:
    """Entrypoint for the CLI application."""
    app()
