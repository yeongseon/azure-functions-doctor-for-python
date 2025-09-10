"""Multi-trigger sample starting with an HTTP trigger.

Additional triggers (timer, queue, etc.) can be added in this file using
decorators (e.g., @app.schedule, @app.queue_trigger).
"""
import azure.functions as func
import logging

app = func.FunctionApp()


@app.route(route="HttpExample", auth_level=func.AuthLevel.Anonymous)
def HttpExample(req: func.HttpRequest) -> func.HttpResponse:  # noqa: N802
    """HTTP trigger (part of multi-trigger sample)."""
    logging.info("v2 multi-trigger HTTP function processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        name = req_body.get("name")
    if name:
        return func.HttpResponse(f"Hello, {name} from multi-trigger sample.")
    return func.HttpResponse(
        "Hello from multi-trigger sample. Pass a name for a personalized response.",
        status_code=200,
    )
