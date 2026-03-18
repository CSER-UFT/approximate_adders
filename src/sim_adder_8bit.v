`timescale 1ns / 1ps

module sim_adder_8bit;

    // DUT sinais
    reg  [7:0] a, b;
    reg        cin;
    wire [7:0] sum;
    wire       cout;

    // Arquivos
    integer in_file;
    integer out_file;
    integer r;
    
    // Clock 100 MHz
    reg clk = 0;
    always #5 clk = ~clk;  // período = 10 ns

    // DUT
    adder_8bit dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    // Caminhos de arquivo de entrada e saída
    reg [1023:0] input_file  = "/home/tiago/energetic_efficiency/data/8bit_all.txt";
    reg [1023:0] output_file = "/home/tiago/energetic_efficiency/results/adder_8bit_results.txt";
    
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

        // lê e aplica vetores na borda do clock
        while (!$feof(in_file)) begin
            @(posedge clk) begin
                r = $fscanf(in_file, "%h %h\n", a, b);
                $fwrite(out_file, "%h %h %b %h %b\n", a, b, cin, sum, cout);
            end
        end 

        $fclose(in_file);
        $fclose(out_file);

        $display("Simulação concluída.");
        $finish;
    end

endmodule
