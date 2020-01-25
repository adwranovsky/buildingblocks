from myhdl import *

@block
def pwm(clk, reset, duty_cycle, pwm_out, rollover):
    """A pulse width modulation block.

    clk -- The clock input
    reset -- The reset signal
    duty_cycle -- The duty cycle. The min and max properties of this signal are
        used to determine the range of the internal counter. The pwm output
        signal flips values when it reaches the value of duty_cycle.
    pwm_out -- The pwm signal. It is flopped once internally to remove any
        glitches that might be present in the combinational logic that
        generates it.
    rollover -- Driven high the cycle before the internal counter rolls back
        over to 0. Useful if one wants to synchronize duty cycle changes right
        on the boundary of a full period.
    """

    pwm_out_glitchy = Signal(intbv(0)[1:])
    count = Signal(modbv(0, min=duty_cycle.min, max=duty_cycle.max))

    @always_comb
    def comb_logic():
        pwm_out_glitchy.next = count < duty_cycle
        rollover.next = count == count.max-1

    @always_seq(clk.posedge, reset=reset)
    def rollover_counter():
        count.next = count + 1

    @always_seq(clk.posedge, reset=reset)
    def flopped_pwm():
        pwm_out.next = pwm_out_glitchy

    return instances()
