`timescale 1ns / 1ps

module herloa_16bit (
    input  [15:0] a,
    input  [15:0] b,
    input         cin,
    output [15:0] sum,
    output        cout
);

    wire c_approx;
    assign c_approx = a[7] & b[7];

    wire [7:0] s_int;
    assign s_int[6:0] = a[6:0] | b[6:0];
    assign s_int[7]   = a[7] ^ b[7];

    wire correction;
    assign correction = a[6] & b[6];

    reg [7:0] sum_approx;
    always @(*) begin
        if (!correction) begin
            sum_approx = s_int;
        end else begin
            if (s_int[7] == 1'b0) begin
                sum_approx[7]   = 1'b1;
                sum_approx[6]   = 1'b0;
                sum_approx[5:0] = s_int[5:0];
            end else begin
                sum_approx[7]   = s_int[7];
                sum_approx[6]   = s_int[6];
                sum_approx[5:0] = 6'b111111;
            end
        end
    end

    assign sum[7:0] = sum_approx;

    rca_8bit high (
        .a(a[15:8]),
        .b(b[15:8]),
        .cin(c_approx),
        .sum(sum[15:8]),
        .cout(cout)
    );

endmodule
