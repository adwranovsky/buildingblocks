#!/usr/bin/env python3

from myhdl import *

from timer import timer
from incrementer import incrementer

class Baud():
    def __init__(self, clk_freq, bitrate):
        self._clk_freq = int(clk_freq)
        self._bitrate = int(bitrate)

    @property
    def bit_period(self):
        return int(self._clk_freq // self._bitrate)

@block
def uart_rx(clk, reset, serial_in, byte_out, valid, baud):
    """A simple UART with a fixed baud rate, one start bit, one stop bit, and no parity bit.
    clk -- The input clock
    reset -- The reset signal
    serial_in -- The serial data signal, it is high when inactive
    byte_out -- The 8 bit deserialized signal
    valid -- Goes high for one clock pulse when byte_out is valid
    baud -- A Baud object, which represents the incoming baud rate of the interface
    """

    t_state = enum("IDLE", "STARTING", "RUNNING")
    state = Signal(t_state.IDLE)

    shift_reg = Signal(intbv(0)[9:])

    # half_bit_timer starts at the beginning of the start bit, and the end of
    # it signals the start of full_bit_timer. It ensures that bits are sampled
    # in the middle.
    half_bit_tstart = Signal(intbv(0)[1:])
    half_bit_done = Signal(intbv(0)[1:])
    half_bit_timer = timer(clk=clk, reset=reset, start=half_bit_tstart, done=half_bit_done, STOP_COUNT=int(baud.bit_period/2))

    # The done signal of full_bit_timer indicates that the next bit should be sampled
    full_bit_tstart = Signal(intbv(0)[1:])
    full_bit_done = Signal(intbv(0)[1:])
    full_bit_timer = timer(clk=clk, reset=reset, start=full_bit_tstart, done=full_bit_done, STOP_COUNT=int(baud.bit_period))

    bit_count = Signal(intbv(0, min=0, max=9)) # 8 data bits + 1 stop bit = max count of 9
    bit_counter = incrementer(clk=clk, reset=reset, inc=full_bit_done, clear=valid, count=bit_count)

    @always_comb
    def fsm_comb_logic():
        valid.next = bit_count == bit_count.max-1 and full_bit_done == 1
        byte_out.next = shift_reg[9:1]
        half_bit_tstart.next = state == t_state.IDLE and serial_in == 0
        full_bit_tstart.next = half_bit_done == 1 or (full_bit_done == 1 and not bit_count == bit_count.max-1)

    @always_seq(clk.posedge, reset=reset)
    def fsm_seq_logic():
        state.next = state
        if state == t_state.IDLE:
            if serial_in == 0:
                state.next = t_state.STARTING
        elif state == t_state.STARTING:
            if half_bit_done == 1:
                state.next = t_state.RUNNING
        elif state == t_state.RUNNING:
            if valid == 1:
                state.next = t_state.IDLE
        else:
            raise ValueError("Undefined state")

    @always_seq(clk.posedge, reset=reset)
    def shift_reg_logic():
        if full_bit_done == 1:
            shift_reg.next = concat(shift_reg[8:], serial_in)
        else:
            shift_reg.next = shift_reg

    return instances()

