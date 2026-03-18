`timescale 1ns / 1ps

module cla_16bit(
    input [15:0] a,
    input [15:0] b,
    input cin,
    output [15:0] sum,
    output cout
);

wire [3:0] PG, GG;
wire [4:0] Cblock;

assign Cblock[0] = cin;
assign Cblock[1] = GG[0] | (PG[0] & Cblock[0]);
assign Cblock[2] = GG[1] | (PG[1] & GG[0]) | (PG[1] & PG[0] & Cblock[0]);
assign Cblock[3] = GG[2] | (PG[2] & GG[1]) | (PG[2] & PG[1] & GG[0]) | (PG[2] & PG[1] & PG[0] & Cblock[0]);
assign Cblock[4] = GG[3] | (PG[3] & GG[2]) | (PG[3] & PG[2] & GG[1]) | (PG[3] & PG[2] & PG[1] & GG[0]) | (PG[3] & PG[2] & PG[1] & PG[0] & Cblock[0]);

cla_4bit u0 (a[3:0],   b[3:0],   Cblock[0], sum[3:0],   , PG[0], GG[0]);
cla_4bit u1 (a[7:4],   b[7:4],   Cblock[1], sum[7:4],   , PG[1], GG[1]);
cla_4bit u2 (a[11:8],  b[11:8],  Cblock[2], sum[11:8],  , PG[2], GG[2]);
cla_4bit u3 (a[15:12], b[15:12], Cblock[3], sum[15:12], , PG[3], GG[3]);

assign cout = Cblock[4];

endmodule