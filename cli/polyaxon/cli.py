import os

import click

from clipped.utils.bools import to_bool

from polyaxon import settings
from polyaxon._services.values import PolyaxonServices
from polyaxon.logger import configure_logger


@click.group()
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Turn on debug logging"
)
def cli(verbose):
    """ Command line interface """
    settings.set_cli_config()
    configure_logger(verbose)


# Init
if PolyaxonServices.is_init():
    from polyaxon._cli.init import init

    cli.add_command(init)

# Notifier
if PolyaxonServices.is_notifier():
    from polyaxon._cli.notifier import notify

    cli.add_command(notify)

# Sidecar
if PolyaxonServices.is_sidecar():
    from polyaxon._cli.sidecar import sidecar

    cli.add_command(sidecar)

# Agent
if PolyaxonServices.is_agent():
    from polyaxon._cli.agent import agent

    cli.add_command(agent)
