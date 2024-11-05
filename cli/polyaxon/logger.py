import logging
import os
import sys

from functools import wraps
from typing import List, Union

from polyaxon import settings
from polyaxon._env_vars.keys import ENV_KEYS_DEBUG, ENV_KEYS_LOG_LEVEL

logger = logging.getLogger("polyaxon.cli")


def configure_logger(verbose):
    if verbose or settings.CLIENT_CONFIG.debug or os.environ.get(ENV_KEYS_DEBUG, False):
        log_level = logging.DEBUG
        os.environ[ENV_KEYS_LOG_LEVEL] = "DEBUG"
        settings.CLIENT_CONFIG.debug = True
    else:
        log_level = (
            logging.DEBUG
            if os.environ.get(ENV_KEYS_LOG_LEVEL) in ["debug", "DEBUG"]
            else logging.INFO
        )
        if settings.CLIENT_CONFIG.log_level:
            log_level = getattr(
                logging, settings.CLIENT_CONFIG.log_level.upper())

    logging.basicConfig(format="%(message)s",
                        level=log_level, stream=sys.stdout)
