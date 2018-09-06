import simpy


class WaterVessel(object):
    """A vessel that holds water that is heated"""

    def __init__(self, env, start_temp, volume):
        self.env = env
        self.cur_temp = start_temp
        self.volume = volume

    def _time_until_temp(self, end_temp):
        """Calculate the required time until the vessel is at a temparture"""

        # TODO: use a real model for this
        # For now assume 1deg/min rise
        return min(0, end_temp - self.cur_temp)

    def _time_until_boil(self):
        """Calculate the required time until the vessel is boiling"""

        return self._time_until_temp(212)

    def warm_to(self, target):
        print("Warming to %d" % target)
        return self.env.timeout(self._time_until_temp(target))


class Kettle(WaterVessel):
    """Representation of a boil kettle"""

    def __init__(self, fill_volume, start_temp):
        super().__init__(self, start_temp, fill_volume)


class HERMS(WaterVessel):
    """Representation of a HERMS mash system"""

    def __init__(self, env, hlt_fill_volume, strike_volume, start_temp):
        super().__init__(self, env, start_temp,
                         hlt_fill_volume + strike_volume)

        self.hlt_fill_volume = hlt_fill_volume
        self.strike_volume = strike_volume


class Chiller(object):
    """Representation of a chiller"""

    def __init__(self, env):
        self.env = env
        self.feed_rate = 10  # rate at which liquid runs through the chiller

    def chill(self, volume):
        yield self.env.timeout(volume / self.feed_rate)


class Batch(object):
    """Representation of a batch"""

    def __init__(self):
        self.name = None
        self.recipe_type = None
        self.batch_size = None
        self.boil_time = None
        self.boil_volume = None
        self.mash_volume = None
        self.action_log = []

    def _log(self, action, time):
        """Write an event entry to the log"""
        print("%s -  %s at %d" % (self.name, action, time))
        self.action_log.append({"time": time, "action": action})

    def brew(self, env, brewery):
        """Simulate a brew of this batch"""
        if self.recipe_type == "Extract":
            for i in self.brew_extract(env, brewery):
                yield i
        else:
            for i in self.brew_ag(env, brewery):
                yield i

    def brew_ag(self, env, brewery):
        """Simulate an all grain brew of this batch"""
        herms_req = brewery.herms.request()
        yield herms_req
        # Python3.3 allows "yield from self.mash(env)", but that breaks
        # flake8 checking.  Right now this slightly more verbose form is
        # preferable if I can retain good linting
        for i in self.mash(env):
            yield i

        # Get a kettle for the sparge
        kettle_req = brewery.kettles.request()
        yield kettle_req

        # Run the sparge
        for i in self.sparge(env):
            yield i

        # All done with the HERMS
        brewery.herms.release(herms_req)

        for i in self.boil(env):
            yield i

        # Get a chiller
        chiller_req = brewery.chiller.request()
        yield chiller_req
        for i in self.chill(env):
            yield i

        # Done with the chiller & the kettle
        brewery.kettles.release(kettle_req)
        brewery.chiller.release(chiller_req)

    def brew_extract(self, env, brewery):
        """Simulate an extract brew of this batch"""
        # Get a kettle
        kettle_req = brewery.kettles.request()
        yield kettle_req

        for i in self.boil(env):
            yield i

        # Get a chiller
        chiller_req = brewery.chiller.request()
        yield chiller_req
        for i in self.chill(env):
            yield i

        # Done with the chiller & the kettle
        brewery.kettles.release(kettle_req)
        brewery.chiller.release(chiller_req)

    def mash(self, env):
        """Mash the batch"""
        self._log("mash start", env.now)
        yield env.timeout(self.mash_time)
        self._log("mash end", env.now)

    def sparge(self, env):
        """Sparge the mash"""
        self._log("sparge start", env.now)
        yield env.timeout(45)
        self._log("sparge end", env.now)

    def boil(self, env):
        """Boil the batch"""
        self._log("boil start", env.now)
        yield env.timeout(self.boil_time)
        self._log("boil end", env.now)

    def chill(self, env):
        """Chill the batch"""
        self._log("chil start", env.now)
        yield env.timeout(self.boil_time)
        self._log("chil end", env.now)


class Brewery(object):
    """A representation of the brewery"""

    def __init__(self, env):
        self.env = env
        self.kettles = simpy.Resource(env, 2)
        self.herms = simpy.Resource(env, 1)
        self.chiller = simpy.Resource(env, 1)
