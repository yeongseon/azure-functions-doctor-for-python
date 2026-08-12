"""HTTP Blueprint: defines the BlueprintExample HTTP trigger.

Import ``bp`` in ``function_app.py`` and call ``app.register_functions(bp)``
to attach these routes to the main application.
"""

import azure.functions as func

bp = func.Blueprint()


@bp.route(route="BlueprintExample", auth_level=func.AuthLevel.Anonymous)
def BlueprintExample(req: func.HttpRequest) -> func.HttpResponse:  # noqa: N802 (Azure style name retained)
    """HTTP trigger — anonymous GET/POST, returns a plain-text success message."""
    return func.HttpResponse("Blueprint-based v2 function executed successfully.", status_code=200)
