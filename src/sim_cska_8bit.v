`timescale 1ns / 1ps

// ============================
// MÓDULO: Carry Skip Adder 8-bit
// ============================
module cska_8bit (
    input  [7:0] a,
    input  [7:0] b,
    input        cin,
    output [7:0] sum,
    output       cout
);

    wire [7:0] p, g;
    wire [8:0] c;

    assign c[0] = cin;

    // Propagate e Generate
    assign p = a ^ b;
    assign g = a & b;

    // ============================
    // BLOCO 0 (bits 0–3)
    // ============================
    wire [4:1] c_block0;

    assign c_block0[1] = g[0] | (p[0] & c[0]);
    assign c_block0[2] = g[1] | (p[1] & c_block0[1]);
    assign c_block0[3] = g[2] | (p[2] & c_block0[2]);
    assign c_block0[4] = g[3] | (p[3] & c_block0[3]);

    wire skip0;
    assign skip0 = p[0] & p[1] & p[2] & p[3];

    assign c[4] = skip0 ? c[0] : c_block0[4];

    // ============================
    // BLOCO 1 (bits 4–7)
    // ============================
    wire [8:5] c_block1;

    assign c_block1[5] = g[4] | (p[4] & c[4]);
    assign c_block1[6] = g[5] | (p[5] & c_block1[5]);
    assign c_block1[7] = g[6] | (p[6] & c_block1[6]);
    assign c_block1[8] = g[7] | (p[7] & c_block1[7]);

    wire skip1;
    assign skip1 = p[4] & p[5] & p[6] & p[7];

    assign c[8] = skip1 ? c[4] : c_block1[8];

    // ============================
    // Soma final
    // ============================
    assign sum = p ^ c[7:0];
    assign cout = c[8];

endmodule


// ============================
// TESTBENCH (inalterado)
// ============================
module sim_cska_8bit;

    reg  [7:0] a, b;
    reg        cin;
    wire [7:0] sum;
    wire       cout;

    integer in_file;
    integer out_file;
    integer r;
    
    ip_8bit dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    reg [1023:0] input_file  = "/home/tiago/energetic_efficiency/data/8bit_all.txt";
    reg [1023:0] output_file = "/home/tiago/energetic_efficiency/results/cska_8bit_results.txt";
    
    initial begin
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

        cin = 0;

        while (!$feof(in_file)) begin
            r = $fscanf(in_file, "%h %h\n", a, b);
            #10;
            $fwrite(out_file, "%h %h %b %h %b\n", a, b, cin, sum, cout);
        end

        $fclose(in_file);
        $fclose(out_file);

        $display("Simulação concluída.");
        $finish;
    end

endmodule
