`timescale 1ns / 1ps

module sim_cla_32bit_exponential;

    reg [31:0] a, b;
    reg cin;
    wire [31:0] sum;
    wire cout;

    // Arquivos
    integer in_file;
    integer out_file;
    integer r;

    cla_32bit dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

        // Caminhos de arquivo de entrada e saída
    reg [1023:0] input_file  = "/home/tiago/energetic_efficiency/data/32_exponential.txt";
    reg [1023:0] output_file = "/home/tiago/energetic_efficiency/results/cla_32bit_exponential.txt";
    
    initial begin
        // Abre arquivos
        in_file  = $fopen(input_file, "r");
        out_file = $fopen(output_file, "w");

        if(in_file == 0) begin
            $display("Erro ao abrir arquivo de entrada: %s", input_file);
            $finish;
        end
        if(out_file == 0) begin
            $display("Erro ao abrir arquivo de saída: %s", output_file);
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
