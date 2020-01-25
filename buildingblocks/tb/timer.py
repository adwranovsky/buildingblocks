import sys
import random

from colorama import Fore, Back, Style
from myhdl import *

from ..rtl.timer import timer
from .utilities import make_runnable

@block
def testbench():
    """A testbench for the timer block"""
    random.seed(24160)

    cycle_count = Signal(intbv(0))
    error_count = Signal(intbv(0))

    rst_n = ResetSignal(0, active=0, isasync=True)
    clk = Signal(bool(0))

    num_duts = 5
    stop_counts = [random.randint(1, 100) for x in range(num_duts)]
    start = [Signal(bool(0)) for x in range(num_duts)]
    done = [Signal(bool(0)) for x in range(num_duts)]
    duts = [
        timer(
            clk=clk,
            reset=rst_n,
            start=start[i],
            done=done[i],
            STOP_COUNT=stop_counts[i]
        ) for i in range(num_duts)
    ]

    @instance
    def tests():
        # Wait for a couple clock signals to deaasert reset
        for x in range(5):
            yield clk.negedge
        rst_n.next = 1

        for i, dut in enumerate(duts):
            # Test the DUT can perform two standalone pulses in sequence
            for x in range(2):
                # Create some space from the last action
                for y in range(5):
                    yield clk.negedge

                # Start the timer and record the time
                start[i].next = 1
                start_cycle = int(cycle_count)
                yield clk.negedge
                start[i].next = 0

                # Wait for the timer to finish
                yield done[i].posedge
                yield delay(1)
                timer_length = cycle_count - start_cycle

                # Check that the timer length is what was expected
                if timer_length == stop_counts[i]:
                    print(
                        Fore.GREEN + "PASSED" + Style.RESET_ALL + " -- "
                        + "timer %d length matched %d"%(i, stop_counts[i])
                    )
                else:
                    error_count.next += 1
                    print(
                        Fore.RED + "FAILED" + Style.RESET_ALL + " -- "
                        + "timer %d length %d, expected %d"%(i, timer_length, stop_counts[i])
                    )

            # Create some space
            for x in range(5):
                yield clk.negedge

            # Test that the DUT can perform 2 consecutive pulses in exactly 2*STOP_COUNT time
            # Start the timer and record the time
            start[i].next = 1
            start_cycle = int(cycle_count)

            # Wait for two done pulses
            for x in range(2):
                yield done[i].posedge
            yield delay(1)
            timer_length = cycle_count - start_cycle

            # Check that the timer length is what was expected
            if timer_length == stop_counts[i] * 2:
                print(
                    Fore.GREEN + "PASSED" + Style.RESET_ALL + " -- "
                    + "timer %d two-pulse length matched %d"%(i, stop_counts[i] * 2)
                )
            else:
                error_count.next += 1
                print(
                    Fore.RED + "FAILED" + Style.RESET_ALL + " -- "
                    + "timer %d two-pulse length %d, expected %d"%(i, timer_length, stop_counts[i] * 2)
                )


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

