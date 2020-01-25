def make_runnable(testbench):
    def run(trace=False):
        tb = testbench()
        tb.config_sim(trace=trace)
        tb.run_sim()
    return run
