`timescale 1ns / 1ps

// ============================
// MÓDULO: Somador simples
// ============================
module ip_32bit (
    input  [31:0] a,
    input  [31:0] b,
    input        cin,
    output [31:0] sum,
    output       cout
);

    assign {cout, sum} = a + b + cin;

endmodule
