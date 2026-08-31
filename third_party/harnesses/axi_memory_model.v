// Deterministic single-outstanding AXI4 memory responder for AGCWS harnesses.
// This is verification infrastructure, not part of the vendored RTL.
module agcws_axi_memory_model #(
  parameter DATA_WIDTH = 32,
  parameter ADDR_WIDTH = 16,
  parameter DEPTH = 16384
) (
  input wire clk, input wire rst,
  input wire [ADDR_WIDTH-1:0] awaddr, input wire [7:0] awlen,
  input wire awvalid, output wire awready,
  input wire [DATA_WIDTH-1:0] wdata, input wire [DATA_WIDTH/8-1:0] wstrb,
  input wire wlast, input wire wvalid, output wire wready,
  output reg [1:0] bresp, output reg bvalid, input wire bready,
  input wire [ADDR_WIDTH-1:0] araddr, input wire [7:0] arlen,
  input wire arvalid, output wire arready,
  output reg [DATA_WIDTH-1:0] rdata, output reg [1:0] rresp,
  output reg rlast, output reg rvalid, input wire rready
);
  localparam STRB_WIDTH = DATA_WIDTH / 8;
  reg [7:0] memory [0:DEPTH-1];
  reg [ADDR_WIDTH-1:0] write_addr, read_addr;
  reg [8:0] write_left, read_left;
  reg write_active, read_active;
  integer i;

  assign awready = !write_active && !bvalid && !rst;
  assign wready = write_active && !rst;
  assign arready = !read_active && !rvalid && !rst;

  always @(posedge clk) begin
    if (rst) begin
      write_active <= 0; read_active <= 0; bvalid <= 0; rvalid <= 0;
      bresp <= 0; rresp <= 0; rlast <= 0; rdata <= 0;
      write_addr <= 0; read_addr <= 0; write_left <= 0; read_left <= 0;
      for (i = 0; i < DEPTH; i = i + 1) memory[i] <= i[7:0];
    end else begin
      if (bvalid && bready) bvalid <= 0;
      if (rvalid && rready) begin
        rvalid <= 0;
        if (read_left <= 1) begin read_active <= 0; read_left <= 0; rlast <= 0; end
        else begin read_left <= read_left - 1; read_addr <= read_addr + STRB_WIDTH; end
      end
      if (awvalid && awready) begin
        write_active <= 1; write_addr <= awaddr; write_left <= awlen + 1;
      end
      if (wvalid && wready) begin
        for (i = 0; i < STRB_WIDTH; i = i + 1)
          if (wstrb[i]) memory[write_addr + i] <= wdata[i*8 +: 8];
        if (write_left <= 1 || wlast) begin
          write_active <= 0; write_left <= 0; bvalid <= 1; bresp <= 0;
        end else begin write_left <= write_left - 1; write_addr <= write_addr + STRB_WIDTH; end
      end
      if (arvalid && arready) begin
        read_active <= 1; read_addr <= araddr; read_left <= arlen + 1;
      end
      if (read_active && !rvalid) begin
        rdata <= {memory[read_addr+3], memory[read_addr+2], memory[read_addr+1], memory[read_addr]};
        rresp <= 0; rlast <= (read_left == 1); rvalid <= 1;
      end
    end
  end
endmodule
