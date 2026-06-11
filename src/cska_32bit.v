`timescale 1ns / 1ps

module cska_32bit (
    input  [31:0] a,
    input  [31:0] b,
    input          cin,
    output [31:0] sum,
    output         cout
);

    wire [31:0] p, g;
    wire [32:0] c; // Barramento global de carries

    assign c[0] = cin;
    assign p = a ^ b;
    assign g = a & b;

    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : BLOCK
            // Fios para os carries internos do RCA de 4 bits
            // c_int[0] é o carry que entra no bloco i
            // c_int[4] é o carry que SAI do RCA (antes do MUX de skip)
            wire [4:1] c_int;
            wire skip;

            // Lógica do RCA interno do bloco
            // O primeiro bit usa o carry de entrada do bloco (c[i*4])
            assign c[i*4 + 1] = g[i*4 + 0] | (p[i*4 + 0] & c[i*4]);
            assign c[i*4 + 2] = g[i*4 + 1] | (p[i*4 + 1] & c[i*4 + 1]);
            assign c[i*4 + 3] = g[i*4 + 2] | (p[i*4 + 2] & c[i*4 + 2]);
            
            // Carry que sairia "normalmente" pelo RCA
            assign c_int[4]   = g[i*4 + 3] | (p[i*4 + 3] & c[i*4 + 3]);

            // Lógica de Skip (Propagate do bloco)
            assign skip = &p[i*4 +: 4];

            // O carry que vai para o PRÓXIMO bloco decide entre o skip ou o RCA
            assign c[i*4 + 4] = skip ? c[i*4] : c_int[4];
        end
    endgenerate

    // Agora todos os bits de c[31:0] estão preenchidos corretamente
    assign sum  = p ^ c[31:0];
    assign cout = c[32];

endmodule
