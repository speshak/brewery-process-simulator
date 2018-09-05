#!/usr/bin/env python3
import simpy
import logging
import brewery.resources
from functools import partial, wraps
from brewery.day import BrewDayLoader
import pprint

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def trace(env, callback):
    def get_wrapper(env_step, callback):
        """Generate the wrapper for env.step()."""
        @wraps(env_step)
        def tracing_step():
            """Call *callback* for the next event if one exist before
            calling ``env.step()``."""
            if len(env._queue):
                t, prio, eid, event = env._queue[0]
                callback(t, prio, eid, event)
            return env_step()

        return tracing_step

        env.step = get_wrapper(env.step, callback)


def run_simulation():
    def monitor(data, t, prio, eid, event):
        data.append((t, eid, type(event)))

    data = []
    monitor = partial(monitor, data)

    env = simpy.Environment()
    trace(env, monitor)

    logger.info("Starting simulation")
    batches = BrewDayLoader().load_day('2018-08-18')
    print("Loaded %d batches" % len(batches))

    system = brewery.resources.Brewery(env)
    for batch in batches:
        env.process(batch.brew(env, system))

    env.run()
    pprint.pprint(data)


if __name__ == '__main__':
    run_simulation()
