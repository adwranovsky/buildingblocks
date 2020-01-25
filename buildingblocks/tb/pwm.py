import sys
import random

from colorama import Fore, Back, Style
from myhdl import *

from .utilities import make_runnable
from ..rtl.pwm import pwm

def count_ones_until(clk, sig, output_count, event):
    while not event():
        yield clk.posedge
        if output_count == output_count.max-1:
            # We've gone past the limit of our counter, so something bad has happened
            return
        output_count.next += sig[1:]

@block
def testbench():
    """A testbench for the pwm block"""
    random.seed(11111111)

    cycle_count = Signal(intbv(0))
    error_count = Signal(intbv(0))

    rst_n = ResetSignal(0, active=0, isasync=True)
    clk = Signal(bool(0))

    # DUT and test signals
    rollover = Signal(intbv(0)[1:])
    flopped_rollover = Signal(intbv(0)[1:])
    pwm_out = Signal(intbv(0)[1:])
    duty_cycle = Signal(intbv(0)[8:])
    dut = pwm(clk=clk, reset=rst_n, duty_cycle=duty_cycle, pwm_out=pwm_out, rollover=rollover)

    # Vector of duty cycles to test
    test_vector = [random.randint(0, duty_cycle.max) for x in range(10)]

    @always(clk.posedge)
    def flopper():
        flopped_rollover.next = rollover

    @instance
    def tests():
        # Wait for a couple clock signals to deaasert reset
        for x in range(5):
            yield clk.negedge

        # Begin tests
        for dc in test_vector:
            # Take the DUT out of reset
            duty_cycle.next = dc
            rst_n.next = 1

            # Wait for two whole periods to complete and count the time it spent high
            ones_count = Signal(intbv(0, min=duty_cycle.min, max=duty_cycle.max))
            yield count_ones_until(clk, pwm_out, ones_count, lambda: flopped_rollover==1)
            time_high = int(ones_count)
            yield count_ones_until(clk, pwm_out, ones_count, lambda: flopped_rollover==1)
            time_high += int(ones_count)

            if time_high != dc*2:
                print(
                    Fore.RED + "FAILED" + Style.RESET_ALL
                    + f" -- Counted {time_high} cycles high when {dc*2} was expected"
                )
                error_count.next += 1
            else:
                print(
                    Fore.RED + "PASSED" + Style.RESET_ALL
                    + f" -- Counted {time_high} cycles high when {dc*2} was expected"
                )

            # Put the dut back in reset for the next test
            yield clk.negedge
            rst_n.next = 0
            yield clk.negedge

        # Simulation finished
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
