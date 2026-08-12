"""Timer trigger Azure Functions Python v2 example.

Runs on a cron schedule (every 5 minutes). Logs whether the execution
is running later than scheduled via the ``past_due`` flag.
"""

import logging

import azure.functions as func

app = func.FunctionApp()


@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)
def TimerExample(timer: func.TimerRequest) -> None:  # noqa: N802 (Azure style name retained)
    """Timer trigger — fires every 5 minutes.

    The ``past_due`` flag is ``True`` when the function missed its scheduled
    start time (e.g. app was offline). Log a warning so it's visible in
    Application Insights or the portal log stream.
    """
    if timer.past_due:
        logging.warning("The timer is running later than expected.")

    logging.info("Timer trigger executed successfully.")
