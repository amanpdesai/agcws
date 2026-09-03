// Flat-port harness for a synthesized aes_cipher_core.
module aes_core_gls;
  logic clk_i = 1'b0, rst_ni = 1'b0;
  logic [2:0] in_valid_i = 3'b100, out_ready_i = 3'b011;
  logic cfg_valid_i = 1'b0;
  logic [1:0] op_i = 2'b01;
  logic [2:0] key_len_i = 3'b001, crypt_i = 3'b100;
  logic prng_reseed_i = 1'b0, entropy_ack_i = 1'b1;
  logic key_clear_i = 1'b0, data_out_clear_i = 1'b0;
  logic alert_fatal_i = 1'b0, force_masks_i = 1'b0;
  logic [255:0] prd_clearing_state_i = '0, state_init_i = '0;
  logic [511:0] prd_clearing_key_i = '0, key_init_i = '0;
  logic [31:0] entropy_i = '0;
  wire [2:0] in_ready_o, out_valid_o, crypt_o, dec_key_gen_o;
  wire prng_reseed_o, key_clear_o, data_out_clear_o, alert_o, entropy_req_o;
  wire [127:0] data_in_mask_o;
  wire [255:0] state_o;
  logic [2:0] dec_key_gen_i = 3'b100;
  always #5 clk_i = ~clk_i;
  aes_cipher_core dut (.*);
  initial begin
    int blocks = 1;
    int pattern = 0, key_len = 128, decrypt = 0, idle = 0;
    void'($value$plusargs("BLOCKS=%d", blocks));
    void'($value$plusargs("PATTERN=%d", pattern));
    void'($value$plusargs("KEYLEN=%d", key_len));
    void'($value$plusargs("DECRYPT=%d", decrypt));
    void'($value$plusargs("IDLE=%d", idle));
    if (pattern < 0 || pattern > 3 || key_len < 128 || key_len > 256)
      $fatal(1, "invalid workload controls");
    state_init_i = '0;
    state_init_i[7:0] = pattern * 8'h55;
    key_len_i = (key_len == 128) ? 3'b001 : (key_len == 192) ? 3'b010 : 3'b100;
    crypt_i = decrypt ? 3'b011 : 3'b100;
    $dumpfile("activity.vcd"); $dumpvars(0, aes_core_gls);
    repeat (4) @(posedge clk_i); rst_ni = 1'b1; repeat (2) @(posedge clk_i);
    repeat (blocks) begin
      cfg_valid_i = 1'b1; crypt_i = 3'b011; in_valid_i = 3'b011;
      @(posedge clk_i); cfg_valid_i = 1'b0; crypt_i = decrypt ? 3'b011 : 3'b100; in_valid_i = 3'b100;
      for (int cycle = 0; cycle < 2000; cycle++) begin
        @(posedge clk_i);
        if (out_valid_o == 3'b011) cycle = 2000;
        if (cycle == 1999)
          $fatal(1, "GLS handshake did not complete: in_ready=%b out_valid=%b", in_ready_o, out_valid_o);
      end
      repeat (idle) @(posedge clk_i);
    end
    $display("AES_GLS_DONE blocks=%0d", blocks); $finish;
  end
endmodule
