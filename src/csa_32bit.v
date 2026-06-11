`timescale 1ns / 1ps

module csa_32bit (
    input  [31:0] a,
    input  [31:0] b,
    input         cin,
    output [31:0] sum,
    output        cout
);

    wire [31:0] sum_csa;
    wire [31:0] carry_csa;

    assign sum_csa   = a ^ b ^ {31'b0, cin};
    assign carry_csa = (a & b) | (a & {31'b0, cin}) | (b & {31'b0, cin});

    assign {cout, sum} = sum_csa + (carry_csa << 1);

endmodule
