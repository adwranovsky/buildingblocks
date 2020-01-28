from myhdl import *

from ..timer import timer
from ..incrementer import incrementer

@block
def tx(clk, reset, serial_out, byte_in, start, done, baud):
    """A simple UART tx module with a fixed baud rate, one start bit, one stop bit, and no parity bit.
    clk -- The input clock
    reset -- The reset signal
    serial_out -- The serial data signal, it is high when inactive
    byte_in -- The 8 bit number to send
    start -- Input, drive high for one clock cycle to signal that byte_in is valid and should begin sending
    done -- Output, is driven high for one clock cycle to signal that the transmitter is done sending
    baud -- A Baud object, which represents the incoming baud rate of the interface
    """

    t_state = enum("IDLE", "BUSY")
    state = Signal(t_state.IDLE)

    # Holds the data that is being sent, including a start bit and a stop bit
    shift_reg = Signal(intbv(0x3ff)[10:])

    # The done signal of full_bit_timer indicates that the last bit was just sent
    full_bit_tstart = Signal(intbv(0)[1:])
    full_bit_done = Signal(intbv(0)[1:])
    full_bit_timer = timer(clk=clk, reset=reset, start=full_bit_tstart, done=full_bit_done, STOP_COUNT=baud.clocks_per_bit)

    # Counts the number of bits sent
    bit_count = Signal(intbv(0, min=0, max=10)) # 8 data bits + 1 start bit + 1 stop bit = max count of 10
    bit_counter = incrementer(clk=clk, reset=reset, inc=full_bit_done, clear=done, count=bit_count)

    @always_comb
    def done_logic():
        done.next = state==t_state.BUSY and bit_count == bit_count.max-1 and full_bit_done

    @always_comb
    def fsm_comb_logic():
        full_bit_tstart.next = (state==t_state.IDLE and start) or (state==t_state.BUSY and (full_bit_done and not done or start and done))
        serial_out.next = shift_reg[0]

    @always_seq(clk.posedge, reset=reset)
    def fsm_seq_logic():
        state.next = state
        shift_reg.next = shift_reg
        if state == t_state.IDLE:
            if start:
                state.next = t_state.BUSY
                shift_reg.next = concat('1', byte_in[8:], '0')
        elif state == t_state.BUSY:
            if full_bit_done:
                shift_reg.next = concat('1', shift_reg[10:1])
            if done:
                if start:
                    shift_reg.next = concat('1', byte_in[8:], '0')
                else:
                    state.next = t_state.IDLE
        else:
            raise ValueError("Undefined state")

    return instances()
