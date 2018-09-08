"""Brewery process resources."""
import math

import simpy


class WaterVessel(object):
    """A vessel that holds water that is heated."""

    def __init__(self, env, start_temp, volume):
        """
        Constructor.

        env - SimPy environment.
        start_temp - Starting temperature of the vessel.
        volume - Volume of vessel.
        """
        self.env = env
        self.cur_temp = start_temp
        self.volume = volume

    def _time_until_temp(self, end_temp):
        """Calculate the required time until the vessel is at a temperature."""
        # TODO: use a real model for this
        # For now assume 1deg/min rise
        return min(0, end_temp - self.cur_temp)

    def _time_until_boil(self):
        """Calculate the required time until the vessel is boiling."""
        return self._time_until_temp(212)

    def warm_to(self, target):
        """Warm vessel to a target temp."""
        print("Warming to %d" % target)
        return self.env.timeout(self._time_until_temp(target))


class Kettle(WaterVessel):
    """Representation of a boil kettle."""

    def __init__(self, fill_volume=0, start_temp=72):
        """Constructor."""
        super().__init__(self, start_temp, fill_volume)
        self.name = None

    def __str__(self):
        """String representation."""
        return self.name


class HERMS(WaterVessel):
    """Representation of a HERMS mash system."""

    def __init__(self, env, hlt_fill_volume, strike_volume, start_temp):
        """
        Constructor.

        env - SimPy environment.
        hlt_fill_volume - The fill level of the HLT
        strike_volume - The volume of water used for str
        start_temp - Starting temperature of vessel/water
        """
        super().__init__(self, env, start_temp,
                         hlt_fill_volume + strike_volume)

        self.hlt_fill_volume = hlt_fill_volume
        self.strike_volume = strike_volume


class Chiller(object):
    """Representation of a chiller."""

    def __init__(self, env):
        """
        Constructor.

        env - SimPy Environment
        """
        self.env = env
        self.feed_rate = 10  # rate at which liquid runs through the chiller

    def chill(self, volume):
        """
        Chill a volume of water.

        volume - volume of water
        """
        yield self.env.timeout(int(math.ceil(volume / self.feed_rate)))


class Batch(object):
    """Representation of a batch."""

    def __init__(self):
        """Constructor."""
        self.env = None
        self.name = None
        self.recipe_type = None
        self.batch_size = None
        self.boil_time = None
        self.boil_volume = None
        self.mash_volume = None
        self.action_log = []
        self.resource_log = []

    def __str__(self):
        """String representation."""
        return "%s - %sGal - %s" % (
            self.name,
            (self.batch_size/128),
            self.recipe_type)

    def _log_action(self, step, start, end):
        """Write an event entry to the log."""
        self.action_log.append({
            "batch": str(self),
            "step": step,
            "start": start,
            "end": end,
        })

    def _log_resource(self, resource, state, time):
        """Write resource usage to the log."""
        self.resource_log.append({
            "batch": str(self),
            "resource": resource,
            "state": state,
            "time": time,
        })

    def brew(self, env, brewery):
        """
        Simulate a brew of this batch.

        env - SimPy Environment
        """
        self.env = env
        print("Brewing %s" % self)

        if self.recipe_type == "Extract":
            yield self.env.process(self.brew_extract(brewery))
        else:
            yield self.env.process(self.brew_ag(brewery))

    def brew_ag(self, brewery):
        """
        Simulate an all grain brew of this batch.

        brewery - Brewery resource
        """
        herms_req = brewery.herms.request()
        yield herms_req
        self._log_resource("HERMS", "use", self.env.now)

        yield self.env.process(self.mash())

        # Get a kettle for the sparge
        kettle = yield brewery.kettles.get()
        self._log_resource(str(kettle), "use", self.env.now)

        # Run the sparge
        yield self.env.process(self.sparge())

        # All done with the HERMS
        brewery.herms.release(herms_req)
        self._log_resource("HERMS", "release", self.env.now)

        yield self.env.process(self.boil())

        # Get a chiller
        chiller_req = brewery.chiller.request()
        yield chiller_req
        self._log_resource("Chiller", "use", self.env.now)
        yield self.env.process(self.chill())

        # Done with the chiller & the kettle
        brewery.kettles.put(kettle)
        brewery.chiller.release(chiller_req)
        self._log_resource(str(kettle), "release", self.env.now)
        self._log_resource("Chiller", "release", self.env.now)

    def brew_extract(self, brewery):
        """
        Simulate an extract brew of this batch.

        brewery - Brewery resource
        """
        # Get a kettle
        kettle = yield brewery.kettles.get()
        self._log_resource(str(kettle), "use", self.env.now)

        yield self.env.process(self.boil())

        # Get a chiller
        chiller_req = brewery.chiller.request()
        yield chiller_req
        self._log_resource("Chiller", "use", self.env.now)
        yield self.env.process(self.chill())

        # Done with the chiller & the kettle
        brewery.kettles.put(kettle)
        brewery.chiller.release(chiller_req)
        self._log_resource(str(kettle), "release", self.env.now)
        self._log_resource("Chiller", "release", self.env.now)

    def mash(self):
        """Mash the batch."""
        start = self.env.now
        yield self.env.timeout(self.mash_time)
        self._log_action("mash", start, self.env.now)

    def sparge(self):
        """Sparge the mash."""
        start = self.env.now
        yield self.env.timeout(45)
        self._log_action("sparge", start, self.env.now)

    def boil(self):
        """Boil the batch."""
        start = self.env.now
        yield self.env.timeout(self.boil_time)
        self._log_action("boil", start, self.env.now)

    def chill(self):
        """Chill the batch."""
        start = self.env.now
        chiller = Chiller(self.env)

        yield self.env.process(chiller.chill(self.boil_volume))

        self._log_action("chill", start, self.env.now)


class Brewery(object):
    """
    A representation of the brewery.

    This mainly is a container to hold the resources used by batches.
    """

    def __init__(self, env, kettle_count):
        """
        Constructor.

        env - SimPy environment
        """
        self.env = env
        self.herms = simpy.Resource(env, 1)
        self.chiller = simpy.Resource(env, 1)

        self.kettles = simpy.Store(env, kettle_count)
        self._add_kettles(kettle_count)

    def _add_kettles(self, capacity):
        for i in range(capacity):
            kettle = Kettle()
            kettle.name = "Kettle %d" % (i + 1)
            self.kettles.put(kettle)
