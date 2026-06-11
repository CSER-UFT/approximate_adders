`timescale 1ns / 1ps

module csla_16bit (
    input  [15:0] a,
    input  [15:0] b,
    input         cin,
    output [15:0] sum,
    output        cout
);

    wire [3:0] sum0;
    wire c4;

    assign {c4, sum[3:0]} = a[3:0] + b[3:0] + cin;

    wire [3:0] sum1_0, sum1_1;
    wire c8_0, c8_1;

    assign {c8_0, sum1_0} = a[7:4] + b[7:4] + 1'b0;
    assign {c8_1, sum1_1} = a[7:4] + b[7:4] + 1'b1;

    wire c8 = c4;
    assign sum[7:4] = c8 ? sum1_1 : sum1_0;

    wire [3:0] sum2_0, sum2_1;
    wire c12_0, c12_1;

    assign {c12_0, sum2_0} = a[11:8] + b[11:8] + 1'b0;
    assign {c12_1, sum2_1} = a[11:8] + b[11:8] + 1'b1;

    wire c12 = c8 ? c8_1 : c8_0;
    assign sum[11:8] = c12 ? sum2_1 : sum2_0;

    wire [3:0] sum3_0, sum3_1;
    wire c16_0, c16_1;

    assign {c16_0, sum3_0} = a[15:12] + b[15:12] + 1'b0;
    assign {c16_1, sum3_1} = a[15:12] + b[15:12] + 1'b1;

    assign sum[15:12] = c12 ? sum3_1 : sum3_0;
    assign cout       = c12 ? c16_1   : c16_0;

endmodule
