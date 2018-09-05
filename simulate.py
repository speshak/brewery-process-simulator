#!/usr/bin/env python3
import simpy
from brewery.day import BrewDayLoader


def run_simulation():
    env = simpy.Environment()

    batches = BrewDayLoader().load_day('2018-08-18')
    print("Loaded %d batches" % len(batches))

    for batch in batches:
        env.process(batch.brew(env, None))

    env.run()


if __name__ == '__main__':
    run_simulation()
