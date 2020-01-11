`timescale 1ns / 1ps

`define IDLE        6'b000001
`define START1      6'b000010
`define START2      6'b000100
`define BIT_HALF1   6'b001000
`define BIT_HALF2   6'b010000
`define STOP        6'b100000

/*
 * A simple UART RX module with a fixed baud rate, 1 start bit, 1 stop bit, and no parity
 * bit. It samples once in the middle of the bit period.
 */
module uart_rx(
    input clk,
    input rst_n,
    input data_in,
    output [7:0] data_out,
    output valid
);

parameter CLK_FREQ        = 100_000_000;
parameter BAUD            = 115200;
parameter HALF_BIT_PERIOD = CLK_FREQ / BAUD / 2;

reg [5:0] state, next_state;
reg [7:0] data_out_reg, next_data_out_reg;
reg [2:0] bit_counter, next_bit_counter;
reg valid_reg;
reg timer_start;
wire timer_done;

assign data_out = data_out_reg;
assign valid = valid_reg;

timer #(.STOP_COUNT(HALF_BIT_PERIOD)) timer(
    .clk(clk),
    .rst_n(rst_n),
    .start(timer_start),
    .done(timer_done)
);

always @(*) begin
    next_state = state;
    next_data_out_reg = data_out_reg;
    next_bit_counter = bit_counter;
    valid_reg = 0;
    timer_start = 1;
    case (state)
    `IDLE: begin
        if (data_in == 1'b0) begin
            // The start bit is beginning.
            next_state = `START1;
        end else begin
            timer_start = 0;
        end
    end
    `START1: begin
        if (timer_done == 1'b1) begin
            next_state = `START2;
        end
    end
    `START2: begin
        if (timer_done == 1'b1) begin
            // Start bit is done, so move onto the first data bit.
            next_state = `BIT_HALF1;
            next_bit_counter = 0;
        end
    end
    `BIT_HALF1: begin
        if (timer_done == 1'b1) begin
            // Sample the next bit.
            next_state = `BIT_HALF2;
            next_bit_counter = bit_counter + 1;
            next_data_out_reg = {data_out_reg[7:1], data_in};
        end
    end
    `BIT_HALF2: begin
        if (timer_done == 1'b1) begin
            if (bit_counter == 3'd7) begin
                valid_reg = 1;
                next_state = `STOP;
            end else begin
                next_state = `BIT_HALF2;
            end
        end
    end
    `STOP: begin
        if (timer_done == 1'b1) begin
            next_state = `IDLE;
            timer_start = 0;
        end
    end
    endcase
end

always @(posedge clk) begin
    if (rst_n == 0) begin
        state <= `IDLE;
        data_out_reg <= 0;
        bit_counter <= 0;
    end else begin
        state <= next_state;
        data_out_reg <= next_data_out_reg;
        bit_counter <= next_bit_counter;
    end
end

endmodule
