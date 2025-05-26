import typer
from azure_function_doctor.doctor import run_diagnostics

app = typer.Typer()


@app.command()
def run():
    """Run the Azure Function diagnostics"""
    run_diagnostics()


def main():
    app()
