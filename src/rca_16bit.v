`timescale 1ns / 1ps

module rca_16bit(
    input [15:0] a,
    input [15:0] b,
    input cin,
    output [15:0] sum,
    output cout
);
    
    wire c8;
    
    rca_8bit low (a[7:0], b[7:0], cin, sum[7:0], c8);
    rca_8bit high (a[15:8], b[15:8], c8, sum[15:8], cout);

endmodule
