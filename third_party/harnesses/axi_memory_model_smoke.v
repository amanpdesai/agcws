`timescale 1ns/1ps
module agcws_axi_memory_model_smoke;
  reg clk=0, rst=1; always #5 clk=~clk;
  reg [15:0] awaddr=0; reg [7:0] awlen=0; reg awvalid=0; wire awready;
  reg [31:0] wdata=0; reg [3:0] wstrb=4'hf; reg wlast=0, wvalid=0; wire wready;
  wire [1:0] bresp; wire bvalid; reg bready=1;
  reg [15:0] araddr=0; reg [7:0] arlen=0; reg arvalid=0; wire arready;
  wire [31:0] rdata; wire [1:0] rresp; wire rlast, rvalid; reg rready=1;
  integer phase=0, beat=0;

  always @(posedge clk) begin
    if (rst) begin phase<=0; beat<=0; awvalid<=0; wvalid<=0; arvalid<=0; end
    else if (phase==0) begin
      awaddr<=16'h0100; awlen<=1; awvalid<=1; phase<=1;
    end else if (phase==1 && awvalid && awready) begin
      awvalid<=0; wdata<=32'h44332211; wlast<=0; wvalid<=1; phase<=2;
    end else if (phase==2 && wvalid && wready) begin
      wdata<=32'h88776655; wlast<=1; beat<=1; phase<=3;
    end else if (phase==3 && wvalid && wready) begin
      wvalid<=0; wlast<=0; phase<=4;
    end else if (phase==4 && !bvalid) begin
      araddr<=16'h0100; arlen<=1; arvalid<=1; phase<=5;
    end else if (phase==5 && arvalid && arready) begin
      arvalid<=0; phase<=6;
    end else if (phase==6 && rvalid && rready) begin
      if (beat==1 && rdata !== 32'h44332211) $fatal(1, "memory read beat 0 mismatch: %h", rdata);
      if (beat==2 && rdata !== 32'h88776655) $fatal(1, "memory read beat 1 mismatch: %h", rdata);
      if (rlast !== (beat==2)) $fatal(1, "memory last mismatch beat=%0d", beat);
      if (beat==2) begin $display("AGCWS_AXI_MEMORY_OK"); $finish; end
      beat<=beat+1;
    end
  end

  initial begin
    #25 rst=0;
    #10000 $fatal(1, "memory model timeout phase=%0d beat=%0d", phase, beat);
  end

  agcws_axi_memory_model #(.DATA_WIDTH(32), .ADDR_WIDTH(16), .DEPTH(16384)) dut (
    .clk(clk), .rst(rst), .awaddr(awaddr), .awlen(awlen), .awvalid(awvalid), .awready(awready),
    .wdata(wdata), .wstrb(wstrb), .wlast(wlast), .wvalid(wvalid), .wready(wready),
    .bresp(bresp), .bvalid(bvalid), .bready(bready), .araddr(araddr), .arlen(arlen),
    .arvalid(arvalid), .arready(arready), .rdata(rdata), .rresp(rresp), .rlast(rlast),
    .rvalid(rvalid), .rready(rready));
endmodule
