"""
CLI entry point for Azure Functions Doctor.

Defines the Click CLI application and commands for running diagnostics and showing the version.
"""

import click

from azure_functions_doctor import __version__
from azure_functions_doctor.doctor import run_diagnostics


@click.group(help="Azure Functions Doctor CLI Tool")
@click.version_option(__version__, prog_name="azure-functions-doctor")
def cli() -> None:
    """Main CLI group."""
    pass


@cli.command(name="run", help="Run the Azure Function diagnostics.")
def run_command() -> None:
    """Run diagnostics logic."""
    run_diagnostics()


def main() -> None:
    """Entrypoint for the CLI application."""
    cli()
