`timescale 1ns / 1ps

module loa_32bit #(
    parameter K = 16
)(
    input  [31:0] a,
    input  [31:0] b,
    input         cin,
    output [31:0] sum,
    output        cout
);

    loa #(
        .N(32),
        .K(K)
    ) core (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

endmodule
