"""Brewery Simulator Module."""
import itertools
from itertools import chain

import simpy

from .api import BrewDayLoader
from .resources import Brewery


def run_simulation(date, permutate=False):
    """Run simulation."""
    batches = BrewDayLoader().load_day(date)

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

        # Collate the log
        full_log = {
            "actions": list(chain.from_iterable(
                [i.action_log for i in batches])),
            "resources": list(chain.from_iterable(
                [i.resource_log for i in batches])),
        }

        return full_log
