`timescale 1ns / 1ps

module sim_herloa_8bit;

    parameter K = 4;

    reg  [7:0] a, b;
    reg        cin;
    wire [7:0] sum;
    wire       cout;

    integer in_file;
    integer out_file;
    integer r;

    reg [4095:0] input_file;
    reg [4095:0] output_file;

    herloa_8bit #(.K(K)) dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    initial begin
        input_file = "./data/8bit_all.txt";
        
        $sformat(output_file, "./sim_output/8bit/k%0d/herloa_8bit.txt", K);

        in_file  = $fopen(input_file, "r");
        out_file = $fopen(output_file, "w");

        if(in_file == 0) begin
            $display("Erro ao abrir arquivo de entrada: %s", input_file);
            $finish;
        end
        if(out_file == 0) begin
            $display("Erro ao abrir arquivo de saida: %s", output_file);
            $finish;
        end

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
