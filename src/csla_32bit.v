`timescale 1ns / 1ps

module csla_32bit (
    input  [31:0] a,
    input  [31:0] b,
    input         cin,
    output [31:0] sum,
    output        cout
);

    wire [32:0] c;
    assign c[0] = cin;

    // Primeiro bloco (RCA real)
    assign {c[4], sum[3:0]} = a[3:0] + b[3:0] + c[0];

    genvar i;
    generate
        for (i = 1; i < 8; i = i + 1) begin : CSLA_BLOCK

            wire [3:0] sum0, sum1;
            wire c0, c1;

            assign {c0, sum0} = a[i*4 +: 4] + b[i*4 +: 4] + 1'b0;
            assign {c1, sum1} = a[i*4 +: 4] + b[i*4 +: 4] + 1'b1;

            assign sum[i*4 +: 4] = c[i*4] ? sum1 : sum0;
            assign c[i*4 + 4]    = c[i*4] ? c1   : c0;

        end
    endgenerate

    assign cout = c[32];

endmodule
