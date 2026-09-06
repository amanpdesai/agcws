`timescale 1ns/1ps
module aes_core_smoke;
  localparam logic [2:0] SP2V_HIGH=3'b011, SP2V_LOW=3'b100;
  localparam logic [2:0] AES_128=3'b001, AES_192=3'b010, AES_256=3'b100;
  localparam logic [1:0] CIPH_FWD=2'b01, CIPH_INV=2'b10;
  logic clk_i=0, rst_ni=0;
  logic [2:0] in_valid_i=SP2V_LOW, out_ready_i=SP2V_HIGH;
  wire [2:0] in_ready_o, out_valid_o, crypt_o, dec_key_gen_o;
  logic cfg_valid_i=0;
  logic [1:0] op_i=CIPH_FWD;
  logic [2:0] key_len_i=AES_128, crypt_i=SP2V_LOW, dec_key_gen_i=SP2V_LOW;
  logic prng_reseed_i=0, key_clear_i=0, data_out_clear_i=0, alert_fatal_i=0;
  logic force_masks_i=0, entropy_ack_i=1;
  logic [31:0] entropy_i=0;
  logic [127:0] prd_clearing_state_i=0;
  logic [255:0] prd_clearing_key_i=0, key_init_i=0;
  logic [127:0] state_init_i [1];
  wire [127:0] state_o [1];
  wire [127:0] data_in_mask_o;
  wire prng_reseed_o, key_clear_o, data_out_clear_o, alert_o, entropy_req_o;
  initial state_init_i[0]='0;
  always #5 clk_i=~clk_i;
  aes_cipher_core dut(.state_init_i(state_init_i[0]), .state_o(state_o[0]), .*);
  `include "aes_transactions.svh"
endmodule
