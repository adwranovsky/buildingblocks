`timescale 1ns / 1ps

module uart_rx_tb();

reg clk;
reg rst_n;
reg data_in;
wire [7:0] data_out;
wire valid;

integer cycle_count;
integer start_cycle_count;
integer total_cycle_count;

integer error_count;
event terminate_sim;

uart_rx #(.HALF_BIT_PERIOD(100)) DUT (
    .clk(clk),
    .rst_n(rst_n),
    .data_in(data_in),
    .data_out(data_out),
    .valid(valid)
);

initial begin
    // Set all signals to known values.
    clk = 0;
    rst_n = 0;
    cycle_count = 0;
    error_count = 0;

    // Generate vcd file for waveform viewing in gtkwave
    $dumpfile("iverilog/uart_rx_tb.vcd");
    $dumpvars(2, uart_rx_tb);

    // Start simulation and deassert reset
    $display("Starting simulation");
    repeat(5) @(negedge clk);
    rst_n = 1;
    repeat(5) @(negedge clk);

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
        error_count = error_count + 1;
        #1 -> terminate_sim;
    end
end

// Call "-> terminate_sim" anywhere to end simulation.
initial begin
    @ (terminate_sim);
    if (error_count == 0) begin
        $display("All tests passed.");
    end else begin
        $display("Failed %0d tests.", error_count);
    end

    #5 $finish;
end

endmodule
