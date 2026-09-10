`timescale 1ns / 1ps

module herloa_32bit (
    input  [31:0] a,
    input  [31:0] b,
    input         cin,
    output [31:0] sum,
    output        cout
);

    wire c_approx;
    assign c_approx = a[15] & b[15];

    wire [15:0] s_int;
    assign s_int[14:0] = a[14:0] | b[14:0];
    assign s_int[15]   = a[15] ^ b[15];

    wire correction;
    assign correction = a[14] & b[14];

    reg [15:0] sum_approx;
    always @(*) begin
        if (!correction) begin
            sum_approx = s_int;
        end else begin
            if (s_int[15] == 1'b0) begin
                sum_approx[15]   = 1'b1;
                sum_approx[14]   = 1'b0;
                sum_approx[13:0] = s_int[13:0];
            end else begin
                sum_approx[15]   = s_int[15];
                sum_approx[14]   = s_int[14];
                sum_approx[13:0] = 14'b11111111111111;
            end
        end
    end

    assign sum[15:0] = sum_approx;

    rca_16bit high (
        .a(a[31:16]),
        .b(b[31:16]),
        .cin(c_approx),
        .sum(sum[31:16]),
        .cout(cout)
    );

endmodule
