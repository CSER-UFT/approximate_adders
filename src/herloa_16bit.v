`timescale 1ns / 1ps

module herloa_16bit #(
    parameter K = 8
)(
    input  [15:0] a,
    input  [15:0] b,
    input         cin,
    output [15:0] sum,
    output        cout
);

    herloa #(.N(16), .K(K)) dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

endmodule
