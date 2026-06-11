`timescale 1ns / 1ps

module ksa_16bit (
    input  [15:0] a,
    input  [15:0] b,
    input          cin,
    output [15:0] sum,
    output         cout
);

    wire [15:0] p, g;
    // Para 16 bits, precisamos de log2(16) = 4 estágios + o estágio inicial (0)
    // Total de 5 níveis: 0, 1, 2, 3, 4
    wire [15:0] G[0:4]; 
    wire [15:0] P[0:4];
    wire [16:0] c;

    assign p = a ^ b;
    assign g = a & b;

    // Estágio 0: Geração e Propagação inicial
    assign G[0] = g;
    assign P[0] = p;

    genvar i, s;
    generate
        // s vai de 1 até 4
        for (s = 1; s <= 4; s = s + 1) begin : STAGE
            for (i = 0; i < 16; i = i + 1) begin : CELL
                if (i < (1 << (s-1))) begin
                    // Buffers para os bits que ainda não têm parceiros à esquerda
                    assign G[s][i] = G[s-1][i];
                    assign P[s][i] = P[s-1][i];
                end else begin
                    // Lógica do Nó de Prefixo Preto (Black Cell)
                    assign G[s][i] = G[s-1][i] | (P[s-1][i] & G[s-1][i-(1<<(s-1))]);
                    assign P[s][i] = P[s-1][i] & P[s-1][i-(1<<(s-1))];
                end
            end
        end
    endgenerate

    assign c[0] = cin;
    
    // O carry final de cada bit vem do último estágio (G[4] e P[4])
    generate
        for (i = 0; i < 16; i = i + 1) begin : CARRY_GEN
            assign c[i+1] = G[4][i] | (P[4][i] & cin);
        end
    endgenerate

    assign sum  = p ^ c[15:0];
    assign cout = c[16];

endmodule
