import logging
import azure.functions as func

def main(msg: func.QueueMessage) -> None:  # noqa: D401
    """Queue trigger logs the message body length."""
    body = msg.get_body().decode("utf-8")
    logging.info("v1 multi-trigger queue message received (%d chars)", len(body))
