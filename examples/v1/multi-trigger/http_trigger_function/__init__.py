import logging
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("v1 multi-trigger HTTP function processed a request.")
    name = req.params.get("name")
    if not name:
        try:
            body = req.get_json()
        except ValueError:
            body = {}
        name = body.get("name")
    if name:
        return func.HttpResponse(f"Hello, {name} from v1 multi-trigger.")
    return func.HttpResponse("Hello from v1 multi-trigger. Pass a name for personalization.")
