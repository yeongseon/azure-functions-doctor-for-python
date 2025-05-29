import json
import traceback

import typer

from azure_functions_doctor.api import run_diagnostics

cli = typer.Typer()


@cli.command()
def diagnose(path: str = ".", json_output: bool = False) -> None:
    """Run diagnostics on an Azure Functions project directory.
    Args:
        path (str): The file system path to the Azure Functions application.
                    Defaults to the current directory.
        json_output (bool): If true, output results in JSON format. Defaults to false.
    Returns:
        None: Prints the results of the diagnostics to the console.
    """
    try:
        results = run_diagnostics(path)

        if json_output:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                symbol = {"pass": "✅", "warn": "⚠️", "fail": "❌"}.get(r["result"], "❓")
                print(f"{symbol} {r['check']}: {r['detail']}")
    except Exception as e:
        print("❌ CLI internal error:", str(e))
        traceback.print_exc()
        raise typer.Exit(code=2) from e


# Register the diagnose command with the CLI
cli.command(name="diagnose", help="Run diagnostics on an Azure Functions project directory.")(
    diagnose
)

if __name__ == "__main__":
    cli()
