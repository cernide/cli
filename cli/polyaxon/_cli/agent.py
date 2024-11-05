import sys
import time
from typing import Optional

import click
from clipped.utils.coroutine import coroutine

from polyaxon import settings
from polxaxon._k8s.agent import Agent
from polxaxon._k8s.agent import Agent
from polyaxon.exceptions import PolyaxonAgentError
from polyaxon.logger import logger


@click.group()
def agent():
    """Command group for Polyaxon agent operations."""
    pass


@agent.command()
@coroutine
async def start():
    """Start the Polyaxon agent."""
    settings.CLIENT_CONFIG.set_agent_header()

    retry = 0
    max_retries = 3
    while retry < max_retries:
        if retry:
            time.sleep(5 * retry)
        try:
            async with Agent(
                owner=None, agent_uuid=None, max_interval=None
            ) as ag:
                await ag.start()
                return
        except Exception as e:
            logger.warning("Polyaxon agent retrying, error %r", e)
            retry += 1

    logger.error(f"Failed to start agent after {max_retries} retries")
    sys.exit(1)


@agent.command()
@click.option(
    "--health-interval",
    type=int,
    help="Health interval between checks.",
)
def healthz(health_interval):
    if not Agent.pong(interval=health_interval):
        logger.warning("Polyaxon agent is not healthy!")
        sys.exit(1)
