from myhdl import *
from buildingblocks.model.uart.baud import Baud
from .. import uart

def tx(baud=Baud(100e6, 1_000_000), **kwargs):
    """Convert the uart.tx module to VHDL or Verilog for synthesis
    baud -- an instance of a baud object, which specifies the target clock speed and baud rate
    """
    clk        = Signal(bool(0))
    reset      = ResetSignal(0, active=0, isasync=True)
    serial_out = Signal(bool(1))
    byte_in    = Signal(intbv(0)[8:])
    start      = Signal(bool(0))
    done       = Signal(bool(0))

    if "name" not in kwargs:
        kwargs["name"] = "uart_tx"

    uart.tx(
        clk=clk,
        reset=reset,
        serial_out=serial_out,
        byte_in=byte_in,
        start=start,
        done=done,
        baud=baud
    ).convert(**kwargs)

def rx(baud=Baud(100e6, 1_000_000), **kwargs):
    """Convert the uart.rx module to VHDL or Verilog for synthesis
    baud -- an instance of a baud object, which specifies the target clock speed and baud rate
    """
    clk        = Signal(bool(0))
    reset      = ResetSignal(0, active=0, isasync=True)
    serial_in  = Signal(bool(1))
    byte_out   = Signal(intbv(0)[8:])
    valid      = Signal(bool(0))

    if "name" not in kwargs:
        kwargs["name"] = "uart_rx"

    uart.rx(
        clk=clk,
        reset=reset,
        serial_in=serial_in,
        byte_out=byte_out,
        valid=valid,
        baud=baud
    ).convert(**kwargs)
