`timescale 1ns / 1ps

module loa_32bit (
    input  [31:0] a,
    input  [31:0] b,
    input         cin,
    output [31:0] sum,
    output        cout
);

    wire c_approx;

    assign sum[15:0] = a[15:0] | b[15:0];
    assign c_approx  = a[15] & b[15];

    rca_16bit high (
        .a(a[31:16]),
        .b(b[31:16]),
        .cin(c_approx),
        .sum(sum[31:16]),
        .cout(cout)
    );

endmodule
