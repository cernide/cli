import os

import click

from clipped.utils.bools import to_bool

from polyaxon import settings
from polyaxon._services.values import PolyaxonServices
from polyaxon.logger import clean_outputs, configure_logger


@click.group()
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Turn on debug logging"
)
@clean_outputs
def cli(verbose):
    """ Command line interface """
    settings.set_cli_config()
    configure_logger(verbose)


# INIT
if PolyaxonServices.is_init():
    from polyaxon._cli.services.init import init

    cli.add_command(init)

# Events
if PolyaxonServices.is_events_handlers():
    from polyaxon._cli.services.notifier import notify

    cli.add_command(notify)

# Sidecar
if PolyaxonServices.is_sidecar():
    from polyaxon._cli.services.sidecar import sidecar

    cli.add_command(sidecar)

# Agents
if PolyaxonServices.is_agent():
    from polyaxon._cli.services.agent import agent

    cli.add_command(agent)
