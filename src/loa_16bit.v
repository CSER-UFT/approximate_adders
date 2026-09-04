`timescale 1ns / 1ps

module loa_16bit (
    input  [15:0] a,
    input  [15:0] b,
    input         cin,
    output [15:0] sum,
    output        cout
);

    assign sum[7:0] = a[7:0] | b[7:0];

    wire c_approx;
    assign c_approx = a[7] & b[7];

    rca_8bit high (
        .a(a[15:8]),
        .b(b[15:8]),
        .cin(c_approx),
        .sum(sum[15:8]),
        .cout(cout)
    );

endmodule
