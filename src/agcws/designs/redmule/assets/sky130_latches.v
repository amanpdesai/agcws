// SKY130 HD negative-level latch: Liberty enable="!GATE_N", data_in="D".
// RedMulE clock gates contain this latch even with LatchBuffers=0.
module \$_DLATCH_N_ (input E, input D, output Q);
  sky130_fd_sc_hd__dlxtn_1 _TECHMAP_REPLACE_ (.GATE_N(E), .D(D), .Q(Q));
endmodule
