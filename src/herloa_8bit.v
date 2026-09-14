`timescale 1ns / 1ps

module herloa_8bit #(
    parameter K = 4
)(
    input  [7:0] a,
    input  [7:0] b,
    input        cin,
    output [7:0] sum,
    output       cout
);

    herloa #(.N(8), .K(K)) dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

endmodule
