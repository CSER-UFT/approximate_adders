`timescale 1ns / 1ps

module cla_8bit (
    input [7:0] a,
    input [7:0] b,
    input cin,
    output [7:0] sum,
    output cout
);

wire [1:0] PG, GG;
wire [2:0] Cblock;

assign Cblock[0] = cin;
assign Cblock[1] = GG[0] | (PG[0] & Cblock[0]);
assign Cblock[2] = GG[1] | (PG[1] & GG[0]) | (PG[1] & PG[0] & Cblock[0]);

cla_4bit low (a[3:0], b[3:0], Cblock[0], sum[3:0], , PG[0], GG[0]);
cla_4bit high (a[7:4], b[7:4], Cblock[1], sum[7:4], , PG[1], GG[1]);

assign cout = Cblock[2];

endmodule
