`timescale 1ns / 1ps

module cla_32bit(
    input [31:0] a,
    input [31:0] b,
    input cin,
    output [31:0] sum,
    output cout
);

wire [7:0] PG, GG;
wire [8:0] Cblock;

assign Cblock[0] = cin;
assign Cblock[1] = GG[0] | (PG[0] & Cblock[0]);
assign Cblock[2] = GG[1] | (PG[1] & GG[0]) | (PG[1] & PG[0] & Cblock[0]);
assign Cblock[3] = GG[2] | (PG[2] & GG[1]) | (PG[2] & PG[1] & GG[0]) | (PG[2] & PG[1] & PG[0] & Cblock[0]);
assign Cblock[4] = GG[3] | (PG[3] & GG[2]) | (PG[3] & PG[2] & GG[1]) | (PG[3] & PG[2] & PG[1] & GG[0]) | (PG[3] & PG[2] & PG[1] & PG[0] & Cblock[0]);
assign Cblock[5] = GG[4] | (PG[4] & GG[3]) | (PG[4] & PG[3] & GG[2]) | (PG[4] & PG[3] & PG[2] & GG[1]) | (PG[4] & PG[3] & PG[2] & PG[1] & GG[0]) | (PG[4] & PG[3] & PG[2] & PG[1] & PG[0] & Cblock[0]);
assign Cblock[6] = GG[5] | (PG[5] & GG[4]) | (PG[5] & PG[4] & GG[3]) | (PG[5] & PG[4] & PG[3] & GG[2]) | (PG[5] & PG[4] & PG[3] & PG[2] & GG[1]) | (PG[5] & PG[4] & PG[3] & PG[2] & PG[1] & GG[0]) | (PG[5] & PG[4] & PG[3] & PG[2] & PG[1] & PG[0] & Cblock[0]);
assign Cblock[7] = GG[6] | (PG[6] & GG[5]) | (PG[6] & PG[5] & GG[4]) | (PG[6] & PG[5] & PG[4] & GG[3]) | (PG[6] & PG[5] & PG[4] & PG[3] & GG[2]) | (PG[6] & PG[5] & PG[4] & PG[3] & PG[2] & GG[1]) | (PG[6] & PG[5] & PG[4] & PG[3] & PG[2] & PG[1] & GG[0]) | (PG[6] & PG[5] & PG[4] & PG[3] & PG[2] & PG[1] & PG[0] & Cblock[0]);
assign Cblock[8] = GG[7] | (PG[7] & GG[6]) | (PG[7] & PG[6] & GG[5]) | (PG[7] & PG[6] & PG[5] & GG[4]) | (PG[7] & PG[6] & PG[5] & PG[4] & GG[3]) | (PG[7] & PG[6] & PG[5] & PG[4] & PG[3] & GG[2]) | (PG[7] & PG[6] & PG[5] & PG[4] & PG[3] & PG[2] & GG[1]) | (PG[7] & PG[6] & PG[5] & PG[4] & PG[3] & PG[2] & PG[1] & GG[0]) | (PG[7] & PG[6] & PG[5] & PG[4] & PG[3] & PG[2] & PG[1] & PG[0] & Cblock[0]);

cla_4bit u0(a[3:0],    b[3:0],    Cblock[0], sum[3:0],    , PG[0], GG[0]);
cla_4bit u1(a[7:4],    b[7:4],    Cblock[1], sum[7:4],    , PG[1], GG[1]);
cla_4bit u2(a[11:8],   b[11:8],   Cblock[2], sum[11:8],   , PG[2], GG[2]);
cla_4bit u3(a[15:12],  b[15:12],  Cblock[3], sum[15:12],  , PG[3], GG[3]);
cla_4bit u4(a[19:16],  b[19:16],  Cblock[4], sum[19:16],  , PG[4], GG[4]);
cla_4bit u5(a[23:20],  b[23:20],  Cblock[5], sum[23:20],  , PG[5], GG[5]);
cla_4bit u6(a[27:24],  b[27:24],  Cblock[6], sum[27:24],  , PG[6], GG[6]);
cla_4bit u7(a[31:28],  b[31:28],  Cblock[7], sum[31:28],  , PG[7], GG[7]);

assign cout = Cblock[8];

endmodule
