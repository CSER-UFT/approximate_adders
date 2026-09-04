`timescale 1ns / 1ps

module heaa_16bit (
    input  [15:0] a,
    input  [15:0] b,
    input         cin,
    output [15:0] sum,
    output        cout
);

    assign sum[6:0] = a[6:0] | b[6:0];

    wire c_approx;
    assign c_approx = a[7] & b[7];

    assign sum[7] = c_approx ? 1'b0 : (a[7] | b[7]);

    rca_8bit high (
        .a(a[15:8]),
        .b(b[15:8]),
        .cin(c_approx),
        .sum(sum[15:8]),
        .cout(cout)
    );

endmodule
