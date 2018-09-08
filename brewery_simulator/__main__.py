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

from .api import BrewDayLoader
from .resources import Brewery

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__version__ = "0.1"


def main():
    """Main entrypoint."""
    arguments = docopt(__doc__, argv=sys.argv[1:], version=__version__)
    run_simulation(
        arguments['<date>'],
        arguments["--permutate"]
    )


def run_simulation(date, permutate=False):
    """Run simulation."""
    batches = BrewDayLoader().load_day(date)
    print("Loaded %d batches" % len(batches))

    if permutate:
        batch_arrangements = itertools.permutations(batches)
    else:
        batch_arrangements = [batches]

    for batches in batch_arrangements:
        env = simpy.Environment()
        system = Brewery(env, 2)

        for batch in batches:
            env.process(batch.brew(env, system))

        env.run()


if __name__ == '__main__':
    main()
