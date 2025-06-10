from functools import partial

from loguru import logger as cli_logger
from . import runmode


def log(level: str, message: str):
    if runmode.state == 'cli':
        cli_logger.log(level, message)


info = partial(log, 'INFO')
debug = partial(log, 'DEBUG')
warning = partial(log, 'WARNING')
error = partial(log, 'ERROR')
critical = partial(log, 'CRITICAL')