`timescale 1ns / 1ps

module ksa_8bit (
    input  [7:0] a,
    input  [7:0] b,
    input        cin,
    output [7:0] sum,
    output       cout
);

    wire [7:0] p, g;
    wire [7:0] G1, P1;
    wire [7:0] G2, P2;
    wire [7:0] G3, P3;
    wire [8:0] c;

    assign p = a ^ b;
    assign g = a & b;

    // Stage 1 (distance 1)
    assign G1[0] = g[0];
    assign P1[0] = p[0];
    genvar i;
    generate
        for (i=1; i<8; i=i+1) begin
            assign G1[i] = g[i] | (p[i] & g[i-1]);
            assign P1[i] = p[i] & p[i-1];
        end
    endgenerate

    // Stage 2 (distance 2)
    assign G2[0] = G1[0];
    assign G2[1] = G1[1];
    assign P2[0] = P1[0];
    assign P2[1] = P1[1];
    generate
        for (i=2; i<8; i=i+1) begin
            assign G2[i] = G1[i] | (P1[i] & G1[i-2]);
            assign P2[i] = P1[i] & P1[i-2];
        end
    endgenerate

    // Stage 3 (distance 4)
    assign G3[0]=G2[0]; assign G3[1]=G2[1];
    assign G3[2]=G2[2]; assign G3[3]=G2[3];
    assign P3[0]=P2[0]; assign P3[1]=P2[1];
    assign P3[2]=P2[2]; assign P3[3]=P2[3];

    generate
        for (i=4; i<8; i=i+1) begin
            assign G3[i] = G2[i] | (P2[i] & G2[i-4]);
            assign P3[i] = P2[i] & P2[i-4];
        end
    endgenerate

    // Carry
    assign c[0] = cin;
    generate
        for (i=0; i<8; i=i+1) begin
            assign c[i+1] = G3[i] | (P3[i] & cin);
        end
    endgenerate

    assign sum = p ^ c[7:0];
    assign cout = c[8];

endmodule

module sim_ksa_8bit;

    reg  [7:0] a, b;
    reg        cin;
    wire [7:0] sum;
    wire       cout;

    integer in_file, out_file, r;

    ksa_8bit dut (
        .a(a), .b(b), .cin(cin),
        .sum(sum), .cout(cout)
    );

    reg [1023:0] input_file  = "/home/tiago/energetic_efficiency/data/8bit_all.txt";
    reg [1023:0] output_file = "/home/tiago/energetic_efficiency/results/ksa_8bit_results.txt";

    initial begin
        // Abre arquivos
        in_file  = $fopen(input_file, "r");
        out_file = $fopen(output_file, "w");

        if(in_file == 0) begin
            $display("Erro ao abrir arquivo de entrada: %s", input_file);
            $finish;
        end
        if(out_file == 0) begin
//             $display("Erro ao abrir arquivo de saída: %s", output_file);
            $finish;
        end

        $display("Simulação iniciada: %s -> %s", input_file, output_file);

        // fixa o carry-in
        cin = 0;

        // Processamento Sequencial Sem Clock Rápido
        while (!$feof(in_file)) begin
            // 1. Lê os dados do arquivo
            r = $fscanf(in_file, "%h %h\n", a, b);
            
            // 2. Aguarda um tempo para a lógica combinacional estabilizar
            // 10ns é mais que suficiente para um RCA de 16 bits na Spartan-7
            #10; 
            
            // 3. Grava a entrada E a saída resultante na mesma linha
            $fwrite(out_file, "%h %h %b %h %b\n", a, b, cin, sum, cout);
        end

        $fclose(in_file);
        $fclose(out_file);

        $display("Simulação concluída.");
        $finish;
    end

endmodule
