#!/usr/bin/env python3
import simpy
import logging
import brewery.resources
from brewery.day import BrewDayLoader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run_simulation():
    env = simpy.Environment()

    logger.info("Starting simulation")
    batches = BrewDayLoader().load_day('2018-08-18')
    print("Loaded %d batches" % len(batches))

    system = brewery.resources.Brewery(env)
    for batch in batches:
        env.process(batch.brew(env, system))

    env.run()


if __name__ == '__main__':
    run_simulation()
