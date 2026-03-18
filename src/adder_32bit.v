`timescale 1ns / 1ps

module adder_32bit(
    input [31:0] a,
    input [31:0] b,
    input cin,
    output [31:0] sum,
    output cout
);

    wire c16;
    
    adder_16bit low (a[15:0], b[15:0], cin, sum[15:0], c16);
    adder_16bit high (a[31:16], b[31:16], c16, sum[31:16], cout);

endmodule
