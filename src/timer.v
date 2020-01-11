`timescale 1ns / 1ps

`define IDLE 1'b0
`define RUNNING 1'b1

module timer(
    input clk,
    input rst_n,
    input start,
    output done
);

parameter STOP_COUNT = 100;

reg state, next_state;
reg [$bits(STOP_COUNT)-1:0] timer, next_timer;
reg done_reg;

assign done = done_reg;

always @(*) begin
    next_state = `IDLE;
    next_timer = 0;
    done_reg = 0;
    case (state)
    `IDLE: begin
        if (start == 1'b1)
            next_state = `RUNNING;
    end
    `RUNNING: begin
        if (timer == STOP_COUNT) begin
            done_reg = 1;
        end else begin
            next_state = `RUNNING;
            next_timer = timer + 1;
        end
    end
    endcase
end

always @(posedge clk) begin
    if (rst_n == 1'b0) begin
        state <= `IDLE;
        timer <= 0;
    end else begin
        state <= next_state;
        timer <= next_timer;
    end
end


endmodule
