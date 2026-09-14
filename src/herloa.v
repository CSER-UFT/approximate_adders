`timescale 1ns / 1ps

module herloa #(
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

    wire [K-1:0] s_int;
    generate
        if (K > 1) begin : gen_s_int_lower
            assign s_int[K-2:0] = a[K-2:0] | b[K-2:0];
        end
    endgenerate
    assign s_int[K-1] = a[K-1] ^ b[K-1];

    wire correction;
    generate
        if (K > 1) begin : gen_corr
            assign correction = a[K-2] & b[K-2];
        end else begin : gen_no_corr
            assign correction = 1'b0;
        end
    endgenerate

    reg [K-1:0] sum_approx;
    always @(*) begin
        if (!correction) begin
            sum_approx = s_int;
        end else begin
            if (s_int[K-1] == 1'b0) begin
                sum_approx[K-1] = 1'b1;
                if (K > 1) sum_approx[K-2] = 1'b0;
                if (K > 2) sum_approx[K-3:0] = s_int[K-3:0];
            end else begin
                sum_approx[K-1] = s_int[K-1];
                if (K > 1) sum_approx[K-2] = s_int[K-2];
                if (K > 2) sum_approx[K-3:0] = {(K-2){1'b1}};
            end
        end
    end

    assign sum[K-1:0] = sum_approx;

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
