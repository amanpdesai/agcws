`timescale 1ns/1ps
module agcws_axi_dma_wr_smoke;
  localparam DW=32; localparam SW=4; localparam AW=16; localparam IW=8;
  localparam LW=20; localparam TW=8; localparam KW=1;
  reg clk=0, rst=1, enable=0, abort=0; always #5 clk=~clk;
  reg [AW-1:0] daddr=0; reg [LW-1:0] dlen=0; reg [TW-1:0] dtag=0; reg dvalid=0; wire dready;
  wire [LW-1:0] slen; wire [TW-1:0] stag; wire [IW-1:0] sid; wire [7:0] sdest; wire [KW-1:0] suser;
  wire [3:0] serr; wire svalid;
  reg [DW-1:0] tdata=0; reg [SW-1:0] tkeep=4'hf; reg tvalid=0, tlast=0;
  reg [IW-1:0] tid=0; reg [7:0] tdest=0; reg [KW-1:0] tuser=0; wire tready;
  wire [IW-1:0] awid; wire [AW-1:0] awaddr; wire [7:0] awlen; wire [2:0] awsize; wire [1:0] awburst;
  wire awlock; wire [3:0] awcache; wire [2:0] awprot; wire awvalid; reg awready=1;
  wire [DW-1:0] wdata; wire [SW-1:0] wstrb; wire wlast,wvalid; reg wready=1;
  reg [IW-1:0] bid=0; reg [1:0] bresp=0; reg bvalid=0; wire bready;
  integer sent=0, written=0, cfg_addr=16'h0200, cfg_len=64; reg aw_seen=0;

  always @(posedge clk) begin
    if (rst) begin dvalid<=0; enable<=0; sent<=0; tvalid<=0; tlast<=0; end
    else if (!enable) enable<=1;
    else if (!dvalid && !sent && dready) begin daddr<=cfg_addr; dlen<=cfg_len; dtag<=8'ha5; dvalid<=1; sent<=1; end
    else begin dvalid<=0; end
  end
  always @(posedge clk) begin
    if (rst) begin tvalid<=0; tlast<=0; tdata<=0; end
    else if (dvalid && dready) begin tvalid<=1; tlast<=0; tdata<=32'h1000; end
    else if (tvalid && tready) begin
      written<=written+1; tdata<=tdata+1;
      if (written==14) begin tlast<=1; end
      else if (tlast) begin tvalid<=0; tlast<=0; end
    end
  end
  always @(posedge clk) if (!rst && svalid) begin
    if (serr!=0 || stag!=8'ha5 || slen!=cfg_len || written!=cfg_len/4)
      $fatal(1,"DMA write failed error=%h tag=%h len=%0d beats=%0d",serr,stag,slen,written);
    $display("AGCWS_AXI_DMA_WR_OK beats=%0d",written); $finish;
  end
  initial begin
    if (!$value$plusargs("ADDR=%d", cfg_addr)) cfg_addr=16'h0200;
    if (!$value$plusargs("LEN=%d", cfg_len)) cfg_len=64;
    $dumpfile("activity.vcd"); $dumpvars(0,agcws_axi_dma_wr_smoke); #25 rst=0; #20000 $fatal(1,"DMA write timeout");
  end

  always @(posedge clk) begin
    if (rst) bvalid<=0;
    else if (awvalid && awready) aw_seen<=1;
    else if (aw_seen && wvalid && wready && wlast) begin bvalid<=1; aw_seen<=0; end
    else if (bvalid && bready) bvalid<=0;
  end
  axi_dma_wr #(.AXI_DATA_WIDTH(DW),.AXI_ADDR_WIDTH(AW),.AXI_STRB_WIDTH(SW),.AXI_ID_WIDTH(IW),
    .AXI_MAX_BURST_LEN(16),.AXIS_DATA_WIDTH(DW),.AXIS_KEEP_ENABLE(1),.AXIS_KEEP_WIDTH(SW),
    .AXIS_LAST_ENABLE(1),.AXIS_ID_ENABLE(1),.AXIS_ID_WIDTH(IW),.AXIS_DEST_ENABLE(0),
    .AXIS_DEST_WIDTH(8),.AXIS_USER_ENABLE(1),.AXIS_USER_WIDTH(KW),.LEN_WIDTH(LW),.TAG_WIDTH(TW),
    .ENABLE_SG(0),.ENABLE_UNALIGNED(0)) dut (
    .clk(clk),.rst(rst),.s_axis_write_desc_addr(daddr),.s_axis_write_desc_len(dlen),.s_axis_write_desc_tag(dtag),
    .s_axis_write_desc_valid(dvalid),.s_axis_write_desc_ready(dready),.m_axis_write_desc_status_len(slen),
    .m_axis_write_desc_status_tag(stag),.m_axis_write_desc_status_id(sid),.m_axis_write_desc_status_dest(sdest),
    .m_axis_write_desc_status_user(suser),.m_axis_write_desc_status_error(serr),.m_axis_write_desc_status_valid(svalid),
    .s_axis_write_data_tdata(tdata),.s_axis_write_data_tkeep(tkeep),.s_axis_write_data_tvalid(tvalid),
    .s_axis_write_data_tready(tready),.s_axis_write_data_tlast(tlast),.s_axis_write_data_tid(tid),
    .s_axis_write_data_tdest(tdest),.s_axis_write_data_tuser(tuser),.m_axi_awid(awid),.m_axi_awaddr(awaddr),
    .m_axi_awlen(awlen),.m_axi_awsize(awsize),.m_axi_awburst(awburst),.m_axi_awlock(awlock),.m_axi_awcache(awcache),
    .m_axi_awprot(awprot),.m_axi_awvalid(awvalid),.m_axi_awready(awready),.m_axi_wdata(wdata),.m_axi_wstrb(wstrb),
    .m_axi_wlast(wlast),.m_axi_wvalid(wvalid),.m_axi_wready(wready),.m_axi_bid(bid),.m_axi_bresp(bresp),
    .m_axi_bvalid(bvalid),.m_axi_bready(bready),.enable(enable),.abort(abort));
endmodule
