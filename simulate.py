#!/usr/bin/env python3
"""
Brewery process simulator.

Usage:
    simulate [--permutate] <date>

Options:
    date          An ISO8601 formatted date
    --permutate   Run the simulation in all possible orders
"""
import itertools
import logging
import sys

import simpy
from docopt import docopt

import brewery.resources
from brewery.api import BrewDayLoader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__version__ = "0.1"


def run_simulation(arg_list):
    """Main entrypoint."""
    arguments = docopt(__doc__, argv=arg_list, version=__version__)

    logger.info("Starting simulation")
    batches = BrewDayLoader().load_day(arguments['<date>'])
    print("Loaded %d batches" % len(batches))

    if arguments["--permutate"]:
        batch_arrangements = itertools.permutations(batches)
    else:
        batch_arrangements = [batches]

    for batches in batch_arrangements:
        env = simpy.Environment()
        system = brewery.resources.Brewery(env)

        for batch in batches:
            env.process(batch.brew(env, system))

        env.run()


if __name__ == '__main__':
    run_simulation(arg_list=sys.argv[1:])
