`timescale 1ns / 1ps

module csa_16bit (
    input  [15:0] a,
    input  [15:0] b,
    input         cin,
    output [15:0] sum,
    output        cout
);

    wire [15:0] sum_csa;
    wire [15:0] carry_csa;

    assign sum_csa   = a ^ b ^ {15'b0, cin};
    assign carry_csa = (a & b) | (a & {15'b0, cin}) | (b & {15'b0, cin});

    assign {cout, sum} = sum_csa + (carry_csa << 1);

endmodule
