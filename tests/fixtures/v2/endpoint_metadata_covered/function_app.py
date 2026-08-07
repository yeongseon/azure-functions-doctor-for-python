# mypy: ignore-errors

import azure.functions as func
from azure_functions_validation import validate_http

app = func.FunctionApp()


@app.route(route="hello")
@validate_http
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("ok")
