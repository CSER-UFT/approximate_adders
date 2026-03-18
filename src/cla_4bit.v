`timescale 1ns / 1ps

module cla_4bit (
    input [3:0] a, b,
    input cin,
    output [3:0] sum,
    output cout,
    output PG, GG
);

    wire [3:0] P, G;
    wire [4:0] c;

    assign c[0] = cin;

    assign P = a ^ b;
    assign G = a & b;

    assign c[1] = G[0] | (P[0] & c[0]);
    assign c[2] = G[1] | (P[1] & G[0]) | (P[1] & P[0] & c[0]);
    assign c[3] = G[2] | (P[2] & G[1]) | (P[2] & P[1] & G[0]) | (P[2] & P[1] & P[0] & c[0]);
    assign c[4] = G[3] | (P[3] & G[2]) | (P[3] & P[2] & G[1]) | (P[3] & P[2] & P[1] & G[0]) | (P[3] & P[2] & P[1] & P[0] & c[0]);

    assign sum = P ^ c[3:0];
    assign cout = c[4];

    assign PG = &P;
    assign GG = G[3] | (P[3] & G[2]) | (P[3] & P[2] & G[1]) | (P[3] & P[2] & P[1] & G[0]);

endmodule
