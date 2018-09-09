#!/usr/bin/env python3
"""
Brewery process simulator.

Usage:
    simulate [--permutate] <date>

Options:
    date          An ISO8601 formatted date
    --permutate   Run the simulation in all possible orders
"""
import logging
import sys

from docopt import docopt

from .__init__ import run_simulation


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__version__ = "0.1"


def main():
    """Main entrypoint."""
    arguments = docopt(__doc__, argv=sys.argv[1:], version=__version__)
    log = run_simulation(
        arguments['<date>'],
        arguments["--permutate"]
    )

    import pprint
    pprint.pprint(log)


if __name__ == '__main__':
    main()
