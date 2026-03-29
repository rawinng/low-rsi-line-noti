import azure.functions as func
import logging
from main import main

app = func.FunctionApp()


@app.timer_trigger(schedule="0 0 22 * * 1-5", arg_name="timer", run_on_startup=False)
def low_rsi_scanner(timer: func.TimerRequest) -> None:
    logging.info("low_rsi_scanner triggered")
    main()
    logging.info("low_rsi_scanner completed")
