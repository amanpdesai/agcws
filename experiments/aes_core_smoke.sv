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

`ifdef AGCWS_GLS
  aes_cipher_core dut (.*);
`else
  aes_cipher_core #(
    .SecMasking(1'b0),
    .SecSBoxImpl(SBoxImplLut),
    .EntropyWidth(EntropyWidth)
  ) dut (.*);
`endif

  initial begin
    static int blocks = 1;
    static int idle_cycles = 0;
    static int pattern = 0;
    static int completed = 0;
    int block_idle;
    string idle_arg;
    logic [127:0] expected_state;
    void'($value$plusargs("BLOCKS=%d", blocks));
    void'($value$plusargs("IDLE=%d", idle_cycles));
    void'($value$plusargs("PATTERN=%d", pattern));
    if (blocks < 1 || blocks > 256 || idle_cycles < 0 || idle_cycles > 10000)
      $fatal(1, "BLOCKS must be in [1,256] and IDLE must be in [0,10000]");
    if (pattern < 0 || pattern > 3) $fatal(1, "PATTERN must be in [0,3]");
    state_init_i[0] = '0;
    state_init_i[0][0][0] = pattern * 8'h55;
    case (pattern)
      0: expected_state = 128'h2e593bd42bfa2c4b344c8ae9ca88ef66;
      1: expected_state = 128'h1796cbe53fe192d3a1a4209cde7688a2;
      2: expected_state = 128'hbaf3c3c5ffe3d92315f2ee90bd726332;
      default: expected_state = 128'h4b1567a5e2477d1a0ece964feb3230db;
    endcase
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
      if (state_o[0] !== expected_state)
        $fatal(1, "unexpected AES-128 result at block %0d: %h", block, state_o[0]);
      if (block == 0) $display("AES_CORE_BLOCK_DONE pattern=%0d state=%h", pattern, state_o[0]);
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
        block_idle = idle_cycles;
        $sformat(idle_arg, "IDLE%0d", block);
        void'($value$plusargs({idle_arg, "=%d"}, block_idle));
        if (block_idle < 0 || block_idle > 10000)
          $fatal(1, "indexed idle cycles out of range");
        repeat (block_idle) @(posedge clk_i);
      end
    end
    $display("AES_CORE_WORKLOAD_DONE blocks=%0d", completed);
    $finish;
  end
endmodule
