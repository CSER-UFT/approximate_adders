`timescale 1ns / 1ps

module hoeraa #(
    parameter N = 8,
    parameter K = 4
)(
    input  [N-1:0] a,
    input  [N-1:0] b,
    input          cin,
    output [N-1:0] sum,
    output         cout
);

    wire c_approx;
    assign c_approx = a[K-1] & b[K-1];

    generate
        if (K == 2) begin : gen_k2
            assign sum[0] = a[0] | b[0];
            assign sum[1] = c_approx ? (a[0] & b[0]) : (a[1] | b[1]);
        end else if (K > 2) begin : gen_kgt2
            assign sum[K-3:0] = {(K-2){1'b1}};
            assign sum[K-2]   = a[K-2] | b[K-2];
            assign sum[K-1]   = c_approx ? (a[K-2] & b[K-2]) : (a[K-1] | b[K-1]);
        end else begin : gen_k1
            assign sum[0] = c_approx ? 1'b0 : (a[0] | b[0]);
        end
    endgenerate

    wire [N-K:0] c_chain;
    assign c_chain[0] = c_approx;

    genvar i;
    generate
        for (i = 0; i < N - K; i = i + 1) begin : gen_fa
            full_adder fa (
                .a(a[K + i]),
                .b(b[K + i]),
                .cin(c_chain[i]),
                .sum(sum[K + i]),
                .cout(c_chain[i + 1])
            );
        end
    endgenerate

    assign cout = c_chain[N - K];

endmodule
