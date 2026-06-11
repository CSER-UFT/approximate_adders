`timescale 1ns / 1ps

module csla_8bit (
    input  [7:0] a,
    input  [7:0] b,
    input        cin,
    output [7:0] sum,
    output       cout
);

    wire [3:0] sum0_0, sum0_1;
    wire c0_0, c0_1;

    wire [3:0] sum1_0, sum1_1;
    wire c1_0, c1_1;

    wire c4;

    // BLOCO 0 (RCA real)
    assign {c4, sum[3:0]} = a[3:0] + b[3:0] + cin;

    // BLOCO 1 (pré-computado)
    assign {c1_0, sum1_0} = a[7:4] + b[7:4] + 1'b0;
    assign {c1_1, sum1_1} = a[7:4] + b[7:4] + 1'b1;

    assign sum[7:4] = c4 ? sum1_1 : sum1_0;
    assign cout     = c4 ? c1_1   : c1_0;

endmodule


module sim_csla_8bit;

    reg  [7:0] a, b;
    reg        cin;
    wire [7:0] sum;
    wire       cout;

    integer in_file, out_file, r;

    csla_8bit dut (
        .a(a), .b(b), .cin(cin),
        .sum(sum), .cout(cout)
    );

    reg [1023:0] input_file  = "/home/tiago/energetic_efficiency/data/8bit_all.txt";
    reg [1023:0] output_file = "/home/tiago/energetic_efficiency/results/csla_8bit_results.txt";

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
