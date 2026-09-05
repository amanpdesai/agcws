task automatic transact(input bit inverse, input bit expand_key);
  while (in_ready_o !== SP2V_HIGH) @(negedge clk_i);
  op_i = inverse ? CIPH_INV : CIPH_FWD;
  cfg_valid_i = 1'b1;
  crypt_i = expand_key ? SP2V_LOW : SP2V_HIGH;
  dec_key_gen_i = expand_key ? SP2V_HIGH : SP2V_LOW;
  in_valid_i = SP2V_HIGH;
  @(negedge clk_i);
  in_valid_i = SP2V_LOW;
  cfg_valid_i = 1'b0;
  crypt_i = SP2V_LOW;
  dec_key_gen_i = SP2V_LOW;
  while (out_valid_o !== SP2V_HIGH) begin
    if (alert_o) $fatal(1, "AES alert during transaction");
    @(negedge clk_i);
  end
endtask

task automatic acknowledge;
  out_ready_i = SP2V_HIGH;
  @(negedge clk_i);
  out_ready_i = SP2V_LOW;
endtask

initial begin
  int fd, fields, command, bits, idle_cycles;
  int completed = 0;
  int cached_dec_bits = 0;
  logic [127:0] data_value, expected_value;
  string program_path;
  if (!$value$plusargs("PROGRAM=%s", program_path)) $fatal(1, "PROGRAM required");
  fd = $fopen(program_path, "r");
  if (!fd) $fatal(1, "cannot open program");
  $dumpfile("activity.vcd");
  $dumpvars(0, aes_core_smoke);
  out_ready_i = SP2V_LOW;
  repeat (4) @(negedge clk_i);
  rst_ni = 1'b1;
  repeat (2) @(negedge clk_i);
  while (!$feof(fd)) begin
    fields = $fscanf(fd, "%d %d %d %h %h\n", command, bits, idle_cycles,
                     data_value, expected_value);
    if (fields != 5) $fatal(1, "malformed transaction program");
    if (command == 0) begin
      repeat (idle_cycles) @(negedge clk_i);
    end else begin
      case (bits)
        128: key_len_i = AES_128;
        192: key_len_i = AES_192;
        256: key_len_i = AES_256;
        default: $fatal(1, "invalid key length");
      endcase
      if (command == 2 && cached_dec_bits != bits) begin
        transact(1'b0, 1'b1);
        acknowledge();
        cached_dec_bits = bits;
      end
      state_init_i[0] = data_value;
      transact(command == 2, 1'b0);
      if (state_o[0] !== expected_value)
        $fatal(1, "AES mismatch block=%0d bits=%0d op=%0d got=%h expected=%h",
               completed, bits, command, state_o[0], expected_value);
      completed++;
      acknowledge();
    end
  end
  $fclose(fd);
  if (alert_o) $fatal(1, "AES alert at completion");
  $display("AES_CORE_WORKLOAD_DONE blocks=%0d", completed);
  $finish;
end
