"""v1 HTTP trigger example (renamed from basic-hello).

Each v1 function resides in its own folder alongside a function.json file.
"""
import logging
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("v1 HttpExample (renamed) processed a request.")
    name = req.params.get("name")
    if not name:
        try:
            body = req.get_json()
        except ValueError:
            body = {}
        name = body.get("name")
    if name:
        return func.HttpResponse(f"Hello, {name}.")
    return func.HttpResponse("Hello from v1 HttpExample. Pass a name for personalization.")
