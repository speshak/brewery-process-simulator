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
        self.batch_size = None
        self.boil_time = None
        self.boil_volume = None
        self.mash_volume = None

    def brew(self, env, brewery):
        with brewery.herms.request() as request:
            yield request

            print("Brewing %s" % self.name)
            yield env.timeout(10)


class Brewery(object):
    """A representation of the brewery"""

    def __init__(self, env):
        self.env = env
        self.kettles = simpy.Resource(env, 2)
        self.herms = simpy.Resource(env, 1)
        self.chiller = simpy.Resource(env, 1)

    def brew(self, batch):
        yield self.env.timeout(10)
        yield batch.brew(self)
        print("Batch %s done at %.2f" % (batch.name, self.env.now))
