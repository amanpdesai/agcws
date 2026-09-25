`ifndef AGCWS_MESH_MAPPED
`include "bsg_defines.sv"
`include "bsg_noc_links.svh"

module agcws_mesh (
  input logic clk_i, reset_i,
  input logic [3:0][65:0] data_i,
  input logic [3:0] valid_i,
  output logic [3:0] ready_o,
  output logic [3:0][65:0] data_o,
  output logic [3:0] valid_o,
  input logic [3:0] ready_i
);
  import bsg_noc_pkg::*;
  `declare_bsg_ready_and_link_sif_s(66, link_s);
  link_s [1:0][1:0][4:0] incoming, outgoing;
  for (genvar y = 0; y < 2; y++) begin: row
    for (genvar x = 0; x < 2; x++) begin: tile
      localparam int port_id = 2*y+x;
      assign incoming[y][x][P].data = data_i[port_id];
      assign incoming[y][x][P].v = valid_i[port_id];
      assign incoming[y][x][P].ready_and_rev = ready_i[port_id];
      assign data_o[port_id] = outgoing[y][x][P].data;
      assign valid_o[port_id] = outgoing[y][x][P].v;
      assign ready_o[port_id] = outgoing[y][x][P].ready_and_rev;
      if (x == 0) assign incoming[y][x][W] = '0;
      else assign incoming[y][x][W] = outgoing[y][x-1][E];
      if (x == 1) assign incoming[y][x][E] = '0;
      else assign incoming[y][x][E] = outgoing[y][x+1][W];
      if (y == 0) assign incoming[y][x][N] = '0;
      else assign incoming[y][x][N] = outgoing[y-1][x][S];
      if (y == 1) assign incoming[y][x][S] = '0;
      else assign incoming[y][x][S] = outgoing[y+1][x][N];
      bsg_mesh_router_buffered #(
        .width_p(66), .x_cord_width_p(1), .y_cord_width_p(1),
        .dims_p(2), .XY_order_p(1), .depopulated_p(1)
      ) router (
        .clk_i(clk_i), .reset_i(reset_i), .link_i(incoming[y][x]),
        .link_o(outgoing[y][x]), .my_x_i(1'(x)), .my_y_i(1'(y))
      );
    end
  end
endmodule
`endif

`ifndef SYNTHESIS
module mesh_temporal;
  timeunit 1ns; timeprecision 1ps;
  logic clk = 0, reset = 1;
  logic [3:0][65:0] source_data = '0, sink_data;
  logic [3:0] source_valid = '0, source_ready, sink_valid, sink_ready = '0;
  agcws_mesh dut (.clk_i(clk), .reset_i(reset), .data_i(source_data),
    .valid_i(source_valid), .ready_o(source_ready), .data_o(sink_data),
    .valid_o(sink_valid), .ready_i(sink_ready));

  int release_cycle[4][4096], queue_id[4][4096], lengths[4], heads[4];
  logic [65:0] expected[4096];
  bit accepted[4096], delivered[4096];
  int count, sent, received, source, dest, release_at, fields, fd;
  int period = 8, pause_cycles = 0;
  logic [31:0] payload;
  string program_path;

  initial begin
    sent = 0;
    received = 0;
    for (int p = 0; p < 4; p++) begin
      lengths[p] = 0;
      heads[p] = 0;
    end
    if (!$value$plusargs("PROGRAM=%s", program_path)) $fatal(1, "PROGRAM required");
    fields = $value$plusargs("SINK_PERIOD=%d", period);
    fields = $value$plusargs("SINK_PAUSE=%d", pause_cycles);
    if (period < 1 || pause_cycles < 0 || pause_cycles >= period) $fatal(1, "invalid sink pacing");
    fd = $fopen(program_path, "r");
    if (!fd) $fatal(1, "cannot open packet program");
    count = 0;
    while (!$feof(fd)) begin
      fields = $fscanf(fd, "%d %d %d %h\n", release_at, source, dest, payload);
      if (fields == -1) break;
      if (fields != 4 || source < 0 || source > 3 || dest < 0 || dest > 3
          || release_at < 0 || release_at >= 8192 || count >= 4096)
        $fatal(1, "invalid packet record");
      if (lengths[source] > 0 && release_at < release_cycle[source][lengths[source]-1])
        $fatal(1, "source release order must be nondecreasing");
      expected[count] = {32'(count), payload, 2'(dest)};
      release_cycle[source][lengths[source]] = release_at;
      queue_id[source][lengths[source]] = count;
      lengths[source]++;
      count++;
    end
    $fclose(fd);
    if (count < 64) $fatal(1, "at least 64 useful packets required");
    $dumpfile("activity.vcd");
    $dumpvars(0, mesh_temporal);
    repeat (8) begin #5; clk = 1; #5; clk = 0; end
    reset = 0;
    for (int cycle = 0; cycle < 8192; cycle++) begin
      for (int p = 0; p < 4; p++) begin
        source_valid[p] = heads[p] < lengths[p] && release_cycle[p][heads[p]] <= cycle;
        source_data[p] = source_valid[p] ? expected[queue_id[p][heads[p]]] : '0;
        sink_ready[p] = ((cycle + p) % period) >= pause_cycles;
      end
      #5;
      for (int p = 0; p < 4; p++) begin
        if (source_valid[p] && source_ready[p]) begin
          accepted[queue_id[p][heads[p]]] = 1;
          heads[p]++;
          sent++;
        end
        if (sink_valid[p] && sink_ready[p]) begin
          int id;
          id = int'(sink_data[p][65:34]);
          if (id < 0 || id >= count || !accepted[id] || delivered[id]
              || sink_data[p] !== expected[id] || int'(sink_data[p][1:0]) != p)
            $fatal(1, "MESH_FUNCTIONAL_MISMATCH cycle=%0d port=%0d id=%0d", cycle, p, id);
          delivered[id] = 1;
          received++;
        end
      end
      clk = 1;
      #5; clk = 0;
    end
    if (sent != count || received != count)
      $fatal(1, "MESH_INCOMPLETE sent=%0d received=%0d expected=%0d", sent, received, count);
    $display("AGCWS_MESH_DONE sent=%0d received=%0d cycles=8200", sent, received);
    $finish;
  end
endmodule
`endif
