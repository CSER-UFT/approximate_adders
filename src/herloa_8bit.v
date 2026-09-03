`timescale 1ns / 1ps

module herloa_8bit (
    input  [7:0] a,
    input  [7:0] b,
    input        cin,
    output [7:0] sum,
    output       cout
);

    wire carry_to_exact;
    assign carry_to_exact = a[3] & b[3];

    // 1. Saída intermediária s_int
    wire [3:0] s_int;
    assign s_int[0] = a[0] | b[0];
    assign s_int[1] = a[1] | b[1];
    assign s_int[2] = a[2] | b[2];
    assign s_int[3] = a[3] ^ b[3];

    // 2. Detecção de carry interno perdido
    wire correction;
    assign correction = a[2] & b[2];

    // 3. Lógica híbrida de correção
    reg [3:0] sum_approx;
    always @(*) begin
        if (!correction) begin
            sum_approx = s_int;
        end else begin
            if (s_int[3] == 1'b0) begin
                // Caso 1: correction == 1 e s_int[3] == 0
                sum_approx[3]   = 1'b1;
                sum_approx[2]   = 1'b0;
                sum_approx[1:0] = s_int[1:0];
            end else begin
                // Caso 2: correction == 1 e s_int[3] == 1
                sum_approx[3]   = s_int[3];
                sum_approx[2]   = s_int[2];
                sum_approx[1:0] = 2'b11;
            end
        end
    end

    assign sum[3:0] = sum_approx;

    // 4. Parte precisa (RCA)
    wire [2:0] c;
    full_adder fa4 (a[4], b[4], carry_to_exact, sum[4], c[0]);
    full_adder fa5 (a[5], b[5], c[0],           sum[5], c[1]);
    full_adder fa6 (a[6], b[6], c[1],           sum[6], c[2]);
    full_adder fa7 (a[7], b[7], c[2],           sum[7], cout);

endmodule
