import sys
import random

from colorama import Fore, Back, Style
from myhdl import *

from ..utilities import make_runnable
from buildingblocks.model.uart.baud import Baud
from buildingblocks.rtl import uart

@block
def testbench():
    """A testbench for uart tx block"""
    random.seed(0xA5A5A5)

    cycle_count = Signal(intbv(0))
    error_count = Signal(intbv(0))

    rst_n = ResetSignal(0, active=0, isasync=True)
    clk = Signal(bool(0))

    baud = Baud(100e6, 1_000_000)
    serial_line = Signal(intbv(1)[1:])
    byte_in, byte_out = (Signal(intbv(0)[8:]) for i in range(2))
    start, done, valid = (Signal(intbv(0)[1:]) for i in range(3))

    # Instantiate a uart rx module to test our tx module. This does depend on
    # our rx module functioning correctly, which is why I wrote the testbench
    # for that first.
    rx_module = uart.rx(
        clk=clk,
        reset=rst_n,
        serial_in=serial_line,
        byte_out=byte_out,
        valid=valid,
        baud=baud
    )

    # Instantiate the DUT
    dut = uart.tx(
        clk=clk,
        reset=rst_n,
        serial_out=serial_line,
        byte_in=byte_in,
        start=start,
        done=done,
        baud=baud
    )

    test_bytes = [random.randint(0, (1<<8)-1) for x in range(10)]

    @instance
    def tests():
        # Wait for a couple clock signals to deaasert reset
        for x in range(5):
            yield clk.negedge
        rst_n.next = 1

        # test each byte
        for byte in test_bytes:
            byte_in.next = byte
            start.next = 1
            yield clk.posedge
            yield clk.negedge
            start.next = 0
            yield valid.posedge
            yield clk.negedge # Not sure why exactly this is needed, but the sim doesn't correctly evaluate the value of byte_out without it
            if byte_out == byte:
                print(Fore.GREEN + "PASSED" + Style.RESET_ALL + f" -- Byte read matched {byte}")
            else:
                print(Fore.RED + "FAILED" + Style.RESET_ALL + f" -- Read {byte_out}, expected {byte}")
                error_count.next += 1
            yield done.posedge

        # Simulation finished
        yield delay(1)
        if error_count == 0:
            print(Fore.GREEN + "All tests passed :)" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed %d tests"%error_count + Style.RESET_ALL)
        raise StopSimulation

    @always(clk.posedge)
    def cycle_counter():
        cycle_count.next += 1
        if cycle_count > 20000:
            print("Hit 20k cycles. Something's wrong.")
            raise StopSimulation

    @always(delay(10))
    def clock_generator():
        clk.next = not clk

    return instances()

run = make_runnable(testbench)
