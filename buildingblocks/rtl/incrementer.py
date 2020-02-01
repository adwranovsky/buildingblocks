from myhdl import *

@block
def incrementer(clk, reset, inc, clear, count):
    """An incrementer circuit with a clear input. When the count reaches its
    maximum value, it saturates and doesn't wrap around.

    clk -- The clock input
    reset -- The reset signal
    inc -- When high, the count increases
    clear -- When high, the count returns to its minimum value
    count -- The current count
    """

    @always_seq(clk.posedge, reset=reset)
    def seq_logc():
        if clear == 1:
            count.next = count.min
        elif count == count.max - 1:
            count.next = count
        elif inc == 1:
            count.next = count + 1
        else:
            count.next = count

    return instances()
