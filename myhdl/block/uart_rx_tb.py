#!/usr/bin/env python3

import sys
import random

from colorama import Fore, Back, Style
from myhdl import *
from uart_rx import *

def uart_tx_model(tx, data, baud):
    """Models a UART with 1 start bit, 8 data bits, and 1 stop bit.
    tx -- serial data output
    data -- the byte to send on tx
    baud -- a baud object that represents the baud rate
    """
    print("-- Transmitting 0x%x" % data)

    print("--- start bit")
    tx.next = 0
    yield delay(baud.bit_period)

    for bit in range(8):
        print("--- %d" % data[bit])
        tx.next = data[bit]
        yield delay(baud.bit_period)

    print("--- stop bit")
    tx.next = 1
    yield delay(baud.bit_period)

@block
def uart_rx_tb():
    """A testbench for the uart rx block"""
    random.seed(0x0a310a31)

    test_bytes = [random.randint(0, (1<<8)-1) for x in range(50)]

    cycle_count = Signal(intbv(0))
    error_count = Signal(intbv(0))

    rst_n = ResetSignal(0, active=0, isasync=True)
    clk = Signal(bool(0))

    tx = Signal(intbv(1)[1:0])
    data_read = Signal(intbv(0)[8:])
    valid = Signal(intbv(0)[1:])

    baud = Baud(100e6, 1_000_000)
    uart = uart_rx(clk=clk, reset=rst_n, serial_in=tx, byte_out=data_read, valid=valid, baud=baud)

    start_tx = Signal(0)
    tx_byte = Signal(intbv(0)[8:0])

    @instance
    def tx_generator():
        while True:
            yield start_tx.posedge
            yield uart_tx_model(tx, tx_byte, baud)
            start_tx.next = 0

    @instance
    def tests():
        # Wait for a couple clock signals to deaasert reset
        for x in range(5):
            yield clk.negedge
        rst_n.next = 1

        # Wait a couple more negative clock edges
        for x in range(5):
            yield clk.negedge

        # Test receiving each byte in the test vector
        for byte in test_bytes:
            tx_byte.next = byte
            start_tx.next = 1
            yield valid.posedge
            yield start_tx.negedge
            if data_read == byte:
                print(
                    Fore.GREEN + "PASSED" + Style.RESET_ALL + " -- "
                    "byte read matched 0x%x" % byte
                )
            else:
                print(
                    Fore.RED + "FAILED" + Style.RESET_ALL + " -- "
                    "read 0x%x, expected 0x%x" % (data_read, byte)
                )
                error_count.next += 1
            yield delay(1)

        # Check errors and end simulation
        if error_count == 0:
            print(Fore.GREEN + "All tests passed :)" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed %d tests"%error_count + Style.RESET_ALL)

        raise StopSimulation

    @always(clk.posedge)
    def cycle_counter():
        cycle_count.next += 1
        if cycle_count > 100_000:
            print("Hit 100k cycles. Something's wrong.")
            raise StopSimulation

    @always(delay(5))
    def clock_generator():
        clk.next = not clk

    return instances()

def run(do_dump):
    tb = uart_rx_tb()
    tb.config_sim(trace=do_dump)
    tb.run_sim()

if __name__ == "__main__":
    try:
        if sys.argv[1] == "-d":
            do_dump = True
    except IndexError:
        do_dump = False
    run(do_dump)
