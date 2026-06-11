`timescale 1ns / 1ps

module ksa_32bit (
    input  [31:0] a,
    input  [31:0] b,
    input          cin,
    output [31:0] sum,
    output         cout
);

    wire [31:0] p, g;
    wire [31:0] G[0:5]; 
    wire [31:0] P[0:5];
    wire [32:0] c;

    assign p = a ^ b;
    assign g = a & b;

    assign G[0] = g;
    assign P[0] = p;

    genvar i, s;
    generate
        for (s = 1; s <= 5; s = s + 1) begin : STAGE
            for (i = 0; i < 32; i = i + 1) begin : CELL
                if (i < (1 << (s-1))) begin
                    assign G[s][i] = G[s-1][i];
                    assign P[s][i] = P[s-1][i];
                end else begin
                    // Lógica da Black Cell - Corrigida
                    assign G[s][i] = G[s-1][i] | (P[s-1][i] & G[s-1][i-(1<<(s-1))]);
                    assign P[s][i] = P[s-1][i] & P[s-1][i-(1<<(s-1))];
                end
            end
        end
    endgenerate

    assign c[0] = cin;
    
    generate
        for (i = 0; i < 32; i = i + 1) begin : CARRY_GEN
            assign c[i+1] = G[5][i] | (P[5][i] & cin);
        end
    endgenerate

    assign sum  = p ^ c[31:0];
    assign cout = c[32];

endmodule
