module aes_core_smoke;
  import aes_pkg::*;

  localparam int NumShares = 1;
  localparam int EntropyWidth = 32;

  logic clk_i = 1'b0;
  logic rst_ni = 1'b0;
  sp2v_e in_valid_i = SP2V_LOW;
  sp2v_e in_ready_o;
  sp2v_e out_valid_o;
  sp2v_e out_ready_i = SP2V_HIGH;
  logic cfg_valid_i = 1'b0;
  ciph_op_e op_i = CIPH_FWD;
  key_len_e key_len_i = AES_128;
  sp2v_e crypt_i = SP2V_LOW;
  sp2v_e crypt_o;
  sp2v_e dec_key_gen_i = SP2V_LOW;
  sp2v_e dec_key_gen_o;
  logic prng_reseed_i = 1'b0;
  logic prng_reseed_o;
  logic key_clear_i = 1'b0;
  logic key_clear_o;
  logic data_out_clear_i = 1'b0;
  logic data_out_clear_o;
  logic alert_fatal_i = 1'b0;
  logic alert_o;
  logic [3:0][3:0][7:0] prd_clearing_state_i [NumShares] = '{default: '0};
  logic [7:0][31:0] prd_clearing_key_i [NumShares] = '{default: '0};
  logic force_masks_i = 1'b0;
  logic [3:0][3:0][7:0] data_in_mask_o;
  logic entropy_req_o;
  logic entropy_ack_i = 1'b1;
  logic [EntropyWidth-1:0] entropy_i = '0;
  logic [3:0][3:0][7:0] state_init_i [NumShares] = '{default: '0};
  logic [7:0][31:0] key_init_i [NumShares] = '{default: '0};
  logic [3:0][3:0][7:0] state_o [NumShares];

  always #5ns clk_i = ~clk_i;

  aes_cipher_core #(
    .SecMasking(1'b0),
    .SecSBoxImpl(SBoxImplLut),
    .EntropyWidth(EntropyWidth)
  ) dut (.*);

  initial begin
    $dumpfile("activity.vcd");
    $dumpvars(0, aes_core_smoke);
    repeat (4) @(posedge clk_i);
    rst_ni = 1'b1;
    repeat (2) @(posedge clk_i);
    cfg_valid_i = 1'b1;
    in_valid_i = SP2V_HIGH;
    repeat (4) @(posedge clk_i);
    in_valid_i = SP2V_LOW;
    cfg_valid_i = 1'b0;
    repeat (80) @(posedge clk_i);
    $finish;
  end
endmodule
