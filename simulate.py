#!/usr/bin/env python3
"""
Brewery process simulator.

Usage:
    simulate <date>

Options:
    date        An ISO8601 formatted date
"""
import logging
import sys

import simpy
from docopt import docopt

import brewery.resources
from brewery.day import BrewDayLoader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__version__ = "0.1"


def run_simulation(arg_list):
    """Main entrypoint."""
    arguments = docopt(__doc__, argv=arg_list, version=__version__)
    env = simpy.Environment()

    logger.info("Starting simulation")
    batches = BrewDayLoader().load_day(arguments['<date>'])
    print("Loaded %d batches" % len(batches))

    system = brewery.resources.Brewery(env)
    for batch in batches:
        env.process(batch.brew(env, system))

    env.run()


if __name__ == '__main__':
    run_simulation(arg_list=sys.argv[1:])
