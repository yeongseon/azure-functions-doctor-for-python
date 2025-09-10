import logging
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:  # Azure Functions v1 entry point
    """Programming Model v1 HTTP trigger function.

    Uses function.json for binding configuration instead of decorators.
    """
    logging.info("v1 HttpExample processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            body = req.get_json()
        except ValueError:
            body = {}
        name = body.get("name")

    if name:
        return func.HttpResponse(
            f"Hello, {name}. This v1 HTTP triggered function executed successfully.",
            status_code=200,
        )

    return func.HttpResponse(
        "This v1 HTTP triggered function executed successfully. Pass a name in the query string or body for a personalized response.",
        status_code=200,
    )
