`timescale 1ns / 1ps

module cska_16bit (
    input  [15:0] a,
    input  [15:0] b,
    input          cin,
    output [15:0] sum,
    output         cout
);

    wire [15:0] p, g;
    wire [16:0] c; // Barramento completo de carries

    assign c[0] = cin;
    assign p = a ^ b;
    assign g = a & b;

    // ============================
    // BLOCO 0 (0–3)
    // ============================
    wire c_out_rca0;
    // Carries internos do RCA
    assign c[1] = g[0] | (p[0] & c[0]);
    assign c[2] = g[1] | (p[1] & c[1]);
    assign c[3] = g[2] | (p[2] & c[2]);
    assign c_out_rca0 = g[3] | (p[3] & c[3]);

    // Lógica de Skip para o próximo bloco
    wire skip0 = &p[3:0];
    assign c[4] = skip0 ? c[0] : c_out_rca0;

    // ============================
    // BLOCO 1 (4–7)
    // ============================
    wire c_out_rca1;
    assign c[5] = g[4] | (p[4] & c[4]);
    assign c[6] = g[5] | (p[5] & c[5]);
    assign c[7] = g[6] | (p[6] & c[6]);
    assign c_out_rca1 = g[7] | (p[7] & c[7]);

    wire skip1 = &p[7:4];
    assign c[8] = skip1 ? c[4] : c_out_rca1;

    // ============================
    // BLOCO 2 (8–11)
    // ============================
    wire c_out_rca2;
    assign c[9]  = g[8]  | (p[8]  & c[8]);
    assign c[10] = g[9]  | (p[9]  & c[9]);
    assign c[11] = g[10] | (p[10] & c[10]);
    assign c_out_rca2 = g[11] | (p[11] & c[11]);

    wire skip2 = &p[11:8];
    assign c[12] = skip2 ? c[8] : c_out_rca2;

    // ============================
    // BLOCO 3 (12–15)
    // ============================
    wire c_out_rca3;
    assign c[13] = g[12] | (p[12] & c[12]);
    assign c[14] = g[13] | (p[13] & c[13]);
    assign c[15] = g[14] | (p[14] & c[14]);
    assign c_out_rca3 = g[15] | (p[15] & c[15]);

    wire skip3 = &p[15:12];
    assign c[16] = skip3 ? c[12] : c_out_rca3;

    // Cálculo final da soma usando o barramento c agora totalmente preenchido
    assign sum  = p ^ c[15:0];
    assign cout = c[16];

endmodule
