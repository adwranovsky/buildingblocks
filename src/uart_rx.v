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

parameter CLK_FREQ   = 100_000_000;
parameter BAUD       = 115200;
parameter BIT_PERIOD = CLK_FREQ / BAUD;

reg [5:0] state, next_state;

always @(*) begin
    next_state = `IDLE;
    case (state)
        `IDLE: begin
        end
        `START1: begin
        end
        `START2: begin
        end
        `BIT_HALF1: begin
        end
        `BIT_HALF2: begin
        end
        `STOP: begin
        end
        default: begin
        end
    endcase
end

always @(posedge clk) begin
    if (rst_n == 0) begin
        state <= `IDLE;
    end else begin
        state <= next_state;
    end
end

endmodule
