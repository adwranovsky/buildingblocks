#!/usr/bin/env python3

from myhdl import *

@block
def timer(clk: Signal, reset: ResetSignal, start: Signal, done: Signal, STOP_COUNT=100):
    """A simple timer with a fixed count length

    clk -- The input clock
    reset -- The reset signal
    start -- When the start signal is high, and the timer isn't already running,
        the timer starts counting
    done -- Goes high for a single clock cycle when the timer is finished counting
    """

    t_state = enum("IDLE", "RUNNING")
    state = Signal(t_state.IDLE)
    timer = Signal(intbv(STOP_COUNT-1, min=0, max=STOP_COUNT))

    @always_comb
    def comb_logic():
        if timer == 0:
            done.next = 1
        else:
            done.next = 0

    @always_seq(clk.posedge, reset=reset)
    def seq_logic():
        if state == t_state.IDLE:
            state.next = t_state.IDLE
            if start == 1:
                state.next = t_state.RUNNING
        elif state == t_state.RUNNING:
            state.next = t_state.RUNNING
            if timer == 0:
                timer.next = STOP_COUNT - 1
                if start == 0:
                    state.next = t_state.IDLE
                else:
                    state.next = t_state.RUNNING
            else:
                timer.next = timer - 1
        else:
            raise ValueError("Undefined state")

    return instances()
