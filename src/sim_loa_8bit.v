`timescale 1ns / 1ps

module sim_loa_8bit #(
    parameter K = 4
);

    // DUT sinais
    reg  [7:0] a, b;
    reg        cin;
    wire [7:0] sum;
    wire       cout;

    // Arquivos
    integer in_file;
    integer out_file;
    integer r;

    // DUT
    loa_8bit #(.K(K)) dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    initial begin
        in_file  = $fopen("./data/8bit_all.txt", "r");
        if (K == 2)
            out_file = $fopen("./sim_output/8bit/k2/loa_8bit.txt", "w");
        else if (K == 6)
            out_file = $fopen("./sim_output/8bit/k6/loa_8bit.txt", "w");
        else
            out_file = $fopen("./sim_output/8bit/k4/loa_8bit.txt", "w");

        if(in_file == 0) begin
            $display("Erro ao abrir arquivo de entrada: ./data/8bit_all.txt");
            $finish;
        end
        if(out_file == 0) begin
            $display("Erro ao abrir arquivo de saida");
            $finish;
        end

        // fixa o carry-in
        cin = 0;

        while (!$feof(in_file)) begin
            r = $fscanf(in_file, "%h %h\n", a, b);
            #10; 
            $fwrite(out_file, "%h %h %b %h %b\n", a, b, cin, sum, cout);
        end

        $fclose(in_file);
        $fclose(out_file);
        $display("Simulacao concluida (K=%0d).", K);
        $finish;
    end

endmodule
