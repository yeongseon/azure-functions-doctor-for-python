"""Multi-trigger Azure Functions Python v2 example.

Demonstrates three common trigger types in a single app:
- HTTP trigger  : synchronous request/response
- Timer trigger : scheduled execution (every 5 minutes)
- Queue trigger : event-driven processing from Azure Storage Queue
"""

import json
import logging

import azure.functions as func

app = func.FunctionApp()


@app.route(route="hello", auth_level=func.AuthLevel.Anonymous)
def http_hello(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger — returns a greeting."""
    logging.info("HTTP trigger processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            body = req.get_json()
        except ValueError:
            body = {}
        name = body.get("name")

    if name:
        return func.HttpResponse(
            json.dumps({"message": f"Hello, {name}!"}),
            mimetype="application/json",
            status_code=200,
        )
    return func.HttpResponse(
        json.dumps({"message": "Hello! Pass a 'name' parameter for a personalized greeting."}),
        mimetype="application/json",
        status_code=200,
    )


@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)
def timer_heartbeat(timer: func.TimerRequest) -> None:
    """Timer trigger — fires every 5 minutes as a heartbeat."""
    if timer.past_due:
        logging.warning("Timer is running later than scheduled.")
    logging.info("Heartbeat timer executed successfully.")


@app.queue_trigger(arg_name="msg", queue_name="tasks", connection="AzureWebJobsStorage")
def queue_processor(msg: func.QueueMessage) -> None:
    """Queue trigger — processes messages from the 'tasks' storage queue."""
    body = msg.get_body().decode("utf-8")
    logging.info("Queue message received: %s", body)

    try:
        payload = json.loads(body)
        logging.info("Processed task: %s", payload)
    except json.JSONDecodeError:
        logging.warning("Queue message is not valid JSON: %s", body)
