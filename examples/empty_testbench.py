import sys
import random

from colorama import Fore, Back, Style
from myhdl import *

# from buildingblocks.rtl.my_block import my_block <---- Import your module here

@block
def testbench():
    """A testbench for my_block"""
    random.seed(11111111)

    cycle_count = Signal(intbv(0))
    error_count = Signal(intbv(0))

    rst_n = ResetSignal(0, active=0, isasync=True)
    clk = Signal(bool(0))

    @instance
    def tests():
        # Wait for a couple clock signals to deaasert reset
        for x in range(5):
            yield clk.negedge
        rst_n.next = 1

        # Add tests here...

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
