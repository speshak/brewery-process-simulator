
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
