#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys

from functools import wraps
from typing import List, Union

from polyaxon.env_vars.keys import EV_KEYS_DEBUG, EV_KEYS_LOG_LEVEL

logger = logging.getLogger("polyaxon.cli")


def configure_logger(verbose):
    # DO NOT MOVE OUTSIDE THE FUNCTION!
    from polyaxon import settings
    from polyaxon.plugins.sentry import set_raven_client

    if verbose or settings.CLIENT_CONFIG.debug or os.environ.get(EV_KEYS_DEBUG, False):
        log_level = logging.DEBUG
        os.environ[EV_KEYS_LOG_LEVEL] = "DEBUG"
        settings.CLIENT_CONFIG.debug = True
    else:
        if not settings.CLIENT_CONFIG.disable_errors_reporting:
            set_raven_client()
        log_level = (
            logging.DEBUG
            if os.environ.get(EV_KEYS_LOG_LEVEL) in ["debug", "DEBUG"]
            else logging.INFO
        )
        if settings.CLIENT_CONFIG.log_level:
            try:
                log_level = logging.getLevelName(
                    settings.CLIENT_CONFIG.log_level.upper()
                )
            except Exception:  # noqa
                pass
    logging.basicConfig(format="%(message)s", level=log_level, stream=sys.stdout)


def clean_outputs(fn):
    """Decorator for CLI with Sentry client handling.
    see https://github.com/getsentry/sentry-python/issues/862#issuecomment-712697356
    """

    @wraps(fn)
    def clean_outputs_wrapper(*args, **kwargs):
        from polyaxon import settings

        cli_config = settings.CLI_CONFIG
        if cli_config and cli_config.log_handler and cli_config.log_handler.dsn:
            import sentry_sdk

            try:
                sentry_sdk.flush()
                return fn(*args, **kwargs)
            except Exception as e:
                sentry_sdk.capture_exception(e)
                sentry_sdk.flush()
                raise e
            finally:
                sentry_sdk.flush()
        else:
            return fn(*args, **kwargs)

    return clean_outputs_wrapper


def not_in_ce(fn):
    """Decorator to show an error when a command not available in CE"""

    @wraps(fn)
    def not_in_ce_wrapper(*args, **kwargs):
        from polyaxon import settings
        from polyaxon.cli.errors import handle_command_not_in_ce

        if not settings.CLI_CONFIG or settings.CLI_CONFIG.is_community:
            handle_command_not_in_ce()
        return fn(*args, **kwargs)

    return not_in_ce_wrapper


def reconfigure_loggers(
    logger_names: List[str],
    log_level: Union[int, str] = logging.WARNING,
    disable: bool = True,
):
    for logger_name in logger_names:
        logging.getLogger(logger_name).setLevel(log_level)
        if disable:
            logging.getLogger(logger_name).disabled = True
