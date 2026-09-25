// Same logical clock period as the pinned Verilator simple-system runtime.
`timescale 1ps/1ps
module ibex_gls;
  bit clk = 0;
  bit rst_n = 1;
  // The pinned C++ runtime has rising edges on even ticks.
  always begin
    #1 clk = 0;
    #1 clk = 1;
  end
  // An explicit falling edge resets flops behind closed clock gates.
  initial begin
    #1 rst_n = 0;
    #7 rst_n = 1;
  end
  ibex_simple_system #(.SRAMInitFile("program.vmem"),
                       .MHPMCounterNum(`AGCWS_MHPM_COUNTER_NUM)) system (
    .IO_CLK(clk), .IO_RST_N(rst_n)
  );
  integer startup;
  reg [95:0] expected_retirement [0:1048575];
  integer retirement_count, retired = 0;
  integer tick_offset = 0;
  initial begin
    if (!$value$plusargs("RETIREMENTS=%d", retirement_count))
      $fatal(1, "missing reference retirement count");
    $readmemh("retirement.vmem", expected_retirement, 0, retirement_count-1);
  end
  always @(posedge clk) begin
    if (system.u_top.rvfi_valid) begin
      if (retired == 0) tick_offset = integer'($time) - integer'(expected_retirement[0][95:64]);
      if (retired >= retirement_count ||
          {system.u_top.rvfi_pc_rdata, system.u_top.rvfi_insn} !== expected_retirement[retired][63:0] ||
          integer'($time) - tick_offset != integer'(expected_retirement[retired][95:64])) begin
        $fwrite(startup, "MISMATCH row=%0d tick=%0t pc=%h insn=%h expected=%h\n",
                retired, $time, system.u_top.rvfi_pc_rdata, system.u_top.rvfi_insn,
                expected_retirement[retired]);
        $fflush();
        $fatal(1, "Ibex GLS differs from reference retirement");
      end
      retired = retired + 1;
    end else if (retired > 0 && retired < retirement_count &&
                 integer'($time) - tick_offset >= integer'(expected_retirement[retired][95:64])) begin
      $fflush();
      $fatal(1, "Ibex GLS missed reference retirement row %0d at %0t", retired, $time);
    end
  end
  initial startup = $fopen("startup.log", "w");
  always @(negedge clk) begin
    if ($time < 40) begin
      $fwrite(startup, "%0t rst=%b req=%b gnt=%b valid=%b addr=%h data=%h core_req=%b core_addr=%h core_valid=%b\n",
              $time, rst_n, system.instr_req, system.instr_gnt,
              system.instr_rvalid, system.instr_addr, system.instr_rdata,
              system.u_top.instr_req_o, system.u_top.instr_addr_o,
              system.u_top.instr_rvalid_i);
      $fflush(startup);
    end
  end
  initial begin
    $dumpfile("sim.fst");
    $dumpvars(0, ibex_gls);
  end
endmodule
