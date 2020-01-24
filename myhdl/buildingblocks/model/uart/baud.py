class Baud():
    """Represents a UART baud rate"""
    def __init__(self, clk_freq, bitrate, TIMESCALE=1e-9):
        self._clk_freq = int(clk_freq)
        self._bitrate = int(bitrate)
        self._timescale = TIMESCALE

    @property
    def clocks_per_bit(self):
        """Gets the number of clock cycles per bit, rounded down to the nearest int"""
        return int(self._clk_freq // self._bitrate)

    @property
    def bit_period(self):
        """Get the length of a bit in units of TIMESCALE, rounded down to the nearest int"""
        return int(self._bitrate**-1 // self._timescale)
