`timescale 1ns / 1ps

`define TIM0_COUNT 7'd101
`define TIM1_COUNT 10'd900

module timer_tb();

reg clk;
reg rst_n;
reg start;
wire [1:0] done;

integer cycle_count;
integer start_cycle_count;
integer total_cycle_count;

integer error_count;
event terminate_sim;

timer #(.STOP_COUNT(`TIM0_COUNT)) DUT0(.clk(clk), .rst_n(rst_n), .start(start), .done(done[0]));
timer #(.STOP_COUNT(`TIM1_COUNT)) DUT1(.clk(clk), .rst_n(rst_n), .start(start), .done(done[1]));

initial begin
    // Set all signals to known values.
    clk = 0;
    rst_n = 0;
    start = 0;
    cycle_count = 0;
    error_count = 0;

    // Generate vcd file for waveform viewing in gtkwave
    $dumpfile("timer.vcd");
    $dumpvars(2, timer_tb);

    // Start simulation and deassert reset
    $display("Starting simulation");
    repeat(5) @(negedge clk);
    rst_n = 1;
    repeat(5) @(negedge clk);

    
    // Test 2 
    repeat(2) begin
        start = 1;
        @(posedge clk) #1 start_cycle_count = cycle_count;
        @(negedge clk) start = 0;

        @(posedge done[0])
        total_cycle_count = cycle_count - start_cycle_count;
        if (total_cycle_count != `TIM0_COUNT)
            error_count = error_count + 1;
        $display(
            "%s -- Timer 0 length: %d",
            total_cycle_count == `TIM0_COUNT ? "PASSED" : "FAILED",
            total_cycle_count
        );

        @(posedge done[1])
        total_cycle_count = cycle_count - start_cycle_count;
        if (total_cycle_count != `TIM1_COUNT)
            error_count = error_count + 1;
        $display(
            "%s -- Timer 1 length: %d",
            total_cycle_count == `TIM1_COUNT ? "PASSED" : "FAILED",
            total_cycle_count
        );

        repeat(20) @(negedge clk);
    end

    #1 -> terminate_sim;

end

// Clock generator
always
    #10 clk <= !clk;

// Clock cycle counter
always @(posedge clk) begin
    cycle_count <= cycle_count + 1;
    if (cycle_count > 20_000) begin
        $display("Hit 20,000 cycles. Is there something wrong?");
        #1 -> terminate_sim;
    end
end

// Call "-> terminate_sim" anywhere to end simulation.
initial begin
    @ (terminate_sim);
    if (error_count == 0) begin
        $display("All tests passed.");
    end else begin
        $display("Failed %d tests.", error_count);
    end

    #5 $finish;
end

endmodule
