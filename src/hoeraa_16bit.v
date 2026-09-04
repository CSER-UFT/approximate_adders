`timescale 1ns / 1ps

module hoeraa_16bit (
    input  [15:0] a,
    input  [15:0] b,
    input         cin,
    output [15:0] sum,
    output        cout
);

    assign sum[5:0] = 6'b111111;
    assign sum[6]   = a[6] | b[6];

    wire c_approx;
    assign c_approx = a[7] & b[7];

    assign sum[7] = c_approx ? (a[6] & b[6]) : (a[7] | b[7]);

    rca_8bit high (
        .a(a[15:8]),
        .b(b[15:8]),
        .cin(c_approx),
        .sum(sum[15:8]),
        .cout(cout)
    );

endmodule
