
class WaterVessel(object):
    """A vessel that holds water that is heated"""

    def __init__(self, start_temp, volume):
        self.cur_temp = start_temp
        self.volume = volume


class Kettle(WaterVessel):
    """Representation of a boil kettle"""

    def __init__(self, fill_volume, start_temp):
        super(start_temp, fill_volume)


class HERMS(WaterVessel):
    """Representation of a HERMS mash system"""

    def __init__(self, hlt_fill_volume, strike_volume, start_temp):
        super(start_temp, hlt_fill_volume + strike_volume)

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
