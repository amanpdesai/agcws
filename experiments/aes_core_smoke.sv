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
    static int blocks = 1;
    static int idle_cycles = 0;
    static int completed = 0;
    void'($value$plusargs("BLOCKS=%d", blocks));
    void'($value$plusargs("IDLE=%d", idle_cycles));
    if (blocks < 1 || blocks > 256 || idle_cycles < 0 || idle_cycles > 10000)
      $fatal(1, "BLOCKS must be in [1,256] and IDLE must be in [0,10000]");
    $dumpfile("activity.vcd");
    $dumpvars(0, aes_core_smoke);
    repeat (4) @(posedge clk_i);
    rst_ni = 1'b1;
    repeat (2) @(posedge clk_i);
    for (int block = 0; block < blocks; block++) begin
      fork
        begin
          wait (out_valid_o == SP2V_HIGH);
          completed++;
          // OpenTitan stores the AES state as [row][column][byte], so this is
          // the NIST zero-key/zero-block vector in packed SV display order.
          if (state_o[0] !== 128'h2e593bd42bfa2c4b344c8ae9ca88ef66)
            $fatal(1, "unexpected AES-128 result at block %0d: %h", block, state_o[0]);
        end
        begin
          cfg_valid_i = 1'b1;
          crypt_i = SP2V_HIGH;
          in_valid_i = SP2V_HIGH;
          @(posedge clk_i);
          in_valid_i = SP2V_LOW;
          cfg_valid_i = 1'b0;
          crypt_i = SP2V_LOW;
          repeat (400) @(posedge clk_i);
          $fatal(1, "AES core did not complete block %0d", block);
        end
      join_any
      disable fork;
      if (block + 1 < blocks) begin
        rst_ni = 1'b0;
        repeat (4) @(posedge clk_i);
        rst_ni = 1'b1;
        repeat (2) @(posedge clk_i);
        repeat (idle_cycles) @(posedge clk_i);
      end
    end
    $display("AES_CORE_WORKLOAD_DONE blocks=%0d", completed);
    $finish;
  end
endmodule
