`timescale 1ns/1ps

module agcws_axi_dma_rd_smoke;
  localparam DW=32; localparam SW=4; localparam AW=16; localparam IW=8;
  localparam LW=20; localparam TW=8; localparam KW=1;
  reg clk=0, rst=1, enable=0;
  always #5 clk = ~clk;

  reg [AW-1:0] desc_addr=0; reg [LW-1:0] desc_len=0; reg [TW-1:0] desc_tag=0;
  reg [IW-1:0] desc_id=0; reg [7:0] desc_dest=0; reg [KW-1:0] desc_user=0;
  reg desc_valid=0; wire desc_ready;
  wire [TW-1:0] status_tag; wire [3:0] status_error; wire status_valid;
  wire [DW-1:0] stream_data; wire [SW-1:0] stream_keep;
  wire stream_valid, stream_last; reg stream_ready=1;
  wire [IW-1:0] stream_id; wire [7:0] stream_dest; wire [KW-1:0] stream_user;
  wire [IW-1:0] arid; wire [AW-1:0] araddr; wire [7:0] arlen;
  wire [2:0] arsize; wire [1:0] arburst; wire arlock; wire [3:0] arcache;
  wire [2:0] arprot; wire arvalid; reg arready=1;
  reg [IW-1:0] rid=0; reg [DW-1:0] rdata=0; reg [1:0] rresp=0;
  reg rlast=0, rvalid=0; wire rready;
  integer beats_left=0, submitted=0, received=0;

  always @(posedge clk) begin
    if (rst) begin
      rvalid <= 0; rlast <= 0; beats_left <= 0;
    end else begin
      if (arvalid && arready) begin
        beats_left <= arlen + 1;
      end
      if (rvalid && rready) begin
        received <= received + 1;
        if (beats_left <= 1) begin rvalid <= 0; rlast <= 0; beats_left <= 0; end
        else begin beats_left <= beats_left - 1; rdata <= rdata + 1; rlast <= (beats_left == 2); end
      end else if (!rvalid && beats_left > 0) begin
        rvalid <= 1; rdata <= {24'h0, received[7:0]}; rlast <= (beats_left == 1);
      end
    end
  end

  always @(posedge clk) begin
    if (rst) begin
      desc_valid <= 0; enable <= 0; submitted <= 0;
    end else if (!submitted && !enable) begin
      enable <= 1;
    end else if (!submitted && desc_ready) begin
      desc_addr <= 16'h0100; desc_len <= 64; desc_tag <= 8'h5a;
      desc_valid <= 1; submitted <= 1;
    end else begin
      desc_valid <= 0;
    end
  end

  always @(posedge clk) begin
    if (!rst && status_valid) begin
      if (status_error != 0 || status_tag != 8'h5a || received != 16)
        $fatal(1, "DMA read failed error=%h tag=%h beats=%0d", status_error, status_tag, received);
      $display("AGCWS_AXI_DMA_RD_OK beats=%0d", received);
      $finish;
    end
  end

  initial begin
    $dumpfile("activity.vcd"); $dumpvars(0, agcws_axi_dma_rd_smoke);
    #25 rst=0;
    #20000 $fatal(1, "DMA read timeout");
  end

  axi_dma_rd #(.AXI_DATA_WIDTH(DW), .AXI_ADDR_WIDTH(AW), .AXI_STRB_WIDTH(SW),
    .AXI_ID_WIDTH(IW), .AXI_MAX_BURST_LEN(16), .AXIS_DATA_WIDTH(DW),
    .AXIS_KEEP_ENABLE(1), .AXIS_KEEP_WIDTH(SW), .AXIS_LAST_ENABLE(1),
    .AXIS_ID_ENABLE(1), .AXIS_ID_WIDTH(IW), .AXIS_DEST_ENABLE(0),
    .AXIS_DEST_WIDTH(8), .AXIS_USER_ENABLE(1), .AXIS_USER_WIDTH(KW),
    .LEN_WIDTH(LW), .TAG_WIDTH(TW), .ENABLE_SG(0), .ENABLE_UNALIGNED(0)) dut (
    .clk(clk), .rst(rst), .s_axis_read_desc_addr(desc_addr),
    .s_axis_read_desc_len(desc_len), .s_axis_read_desc_tag(desc_tag),
    .s_axis_read_desc_id(desc_id), .s_axis_read_desc_dest(desc_dest),
    .s_axis_read_desc_user(desc_user), .s_axis_read_desc_valid(desc_valid),
    .s_axis_read_desc_ready(desc_ready), .m_axis_read_desc_status_tag(status_tag),
    .m_axis_read_desc_status_error(status_error), .m_axis_read_desc_status_valid(status_valid),
    .m_axis_read_data_tdata(stream_data), .m_axis_read_data_tkeep(stream_keep),
    .m_axis_read_data_tvalid(stream_valid), .m_axis_read_data_tready(stream_ready),
    .m_axis_read_data_tlast(stream_last), .m_axis_read_data_tid(stream_id),
    .m_axis_read_data_tdest(stream_dest), .m_axis_read_data_tuser(stream_user),
    .m_axi_arid(arid), .m_axi_araddr(araddr), .m_axi_arlen(arlen), .m_axi_arsize(arsize),
    .m_axi_arburst(arburst), .m_axi_arlock(arlock), .m_axi_arcache(arcache),
    .m_axi_arprot(arprot), .m_axi_arvalid(arvalid), .m_axi_arready(arready),
    .m_axi_rid(rid), .m_axi_rdata(rdata), .m_axi_rresp(rresp), .m_axi_rlast(rlast),
    .m_axi_rvalid(rvalid), .m_axi_rready(rready), .enable(enable));
endmodule
