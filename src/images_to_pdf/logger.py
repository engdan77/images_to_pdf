import datetime
from functools import partial

from loguru import logger as cli_logger
from pywebio_battery import logbox_append

from . import runmode
from pywebio.output import put_text
import datetime


def log(level: str, message: str):
    match runmode.state:
        case "cli":
            cli_logger.log(level, message)
        case "gui":
            now = datetime.datetime.now().strftime("%H:%M:%S")
            logbox_append("log", f"{now} {level} {message}\n")


info = partial(log, "INFO")
debug = partial(log, "DEBUG")
warning = partial(log, "WARNING")
error = partial(log, "ERROR")
critical = partial(log, "CRITICAL")
