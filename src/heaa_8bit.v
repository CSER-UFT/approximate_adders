`timescale 1ns / 1ps

module heaa_8bit (
    input  [7:0] a,
    input  [7:0] b,
    input        cin,
    output [7:0] sum,
    output       cout
);

    wire carry_to_exact;
    assign carry_to_exact = a[3] & b[3];

    // K=4
    assign sum[0] = a[0] | b[0];
    assign sum[1] = a[1] | b[1];
    assign sum[2] = a[2] | b[2];
    assign sum[3] = carry_to_exact ? 1'b0 : (a[3] | b[3]);

    wire [2:0] c;
    full_adder fa4 (a[4], b[4], carry_to_exact, sum[4], c[0]);
    full_adder fa5 (a[5], b[5], c[0],           sum[5], c[1]);
    full_adder fa6 (a[6], b[6], c[1],           sum[6], c[2]);
    full_adder fa7 (a[7], b[7], c[2],           sum[7], cout);

endmodule
