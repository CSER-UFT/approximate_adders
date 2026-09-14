`timescale 1ns/1ps

module sim_loa_16bit_exponential #(
    parameter K = 8
);

    reg  [15:0] a, b;
    reg cin;
    wire [15:0] sum;
    wire cout;

    integer in_file;
    integer out_file;
    integer r;
    
    loa_16bit #(.K(K)) dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    reg [4095:0] input_file;
    reg [4095:0] output_file;
    
    initial begin
        if (!$value$plusargs("INPUT=%s", input_file))
            input_file = "./data/16_exponential.txt";
        if (!$value$plusargs("OUTPUT=%s", output_file)) begin
            if (K == 4)
                output_file = "./sim_output/16bit/k4/loa_16bit_exponential.txt";
            else if (K == 12)
                output_file = "./sim_output/16bit/k12/loa_16bit_exponential.txt";
            else
                output_file = "./sim_output/16bit/k8/loa_16bit_exponential.txt";
        end

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

        $display("Simulacao iniciada (K=%0d): %s -> %s", K, input_file, output_file);

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
