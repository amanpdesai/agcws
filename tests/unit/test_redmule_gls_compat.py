"""Real simulator comparisons against pinned official UDP truth tables."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from agcws.designs.ibex.compat import functional_primitives as ibex_primitives
from agcws.designs.redmule.compat import functional_primitives


def test_unknown_primitive_revision_rejected():
    with pytest.raises(ValueError, match="revision"):
        functional_primitives(b"different model")


@pytest.mark.parametrize('convert', [functional_primitives, ibex_primitives])
def test_udp_equivalence_iverilog(tmp_path, convert):
    source = Path(os.environ.get("AGCWS_SKY130_PRIMITIVES",
        "out/tools/opensta-a9a3f30/source/examples/sky130_hd_primitives.v"))
    if not source.exists() or not shutil.which("iverilog"):
        pytest.skip("pinned SKY130 primitives and Icarus required")
    adapted = tmp_path / "adapted.v"
    adapted.write_text(convert(source.read_bytes()).replace(
        "sky130_fd_sc_hd__", "adapted__").replace("SKY130_FD_SC_HD__", "ADAPTED__"))
    tb = tmp_path / "tb.sv"
    tb.write_text("""module tb;
  reg d=0, clk=0, control=0;
  reg [5:0] m=0;
  wire [6:0] ref_q, dut_q;
  sky130_fd_sc_hd__udp_dff$P p(ref_q[6],d,clk);
  adapted__udp_dff$P q(dut_q[6],d,clk);
  sky130_fd_sc_hd__udp_dff$PR a(ref_q[0],d,clk,control);
  adapted__udp_dff$PR b(dut_q[0],d,clk,control);
  sky130_fd_sc_hd__udp_dff$PS c(ref_q[1],d,clk,control);
  adapted__udp_dff$PS e(dut_q[1],d,clk,control);
  sky130_fd_sc_hd__udp_dlatch$P f(ref_q[2],d,control);
  adapted__udp_dlatch$P g(dut_q[2],d,control);
  sky130_fd_sc_hd__udp_mux_2to1 h(ref_q[3],m[0],m[1],m[4]);
  adapted__udp_mux_2to1 i(dut_q[3],m[0],m[1],m[4]);
  sky130_fd_sc_hd__udp_mux_2to1_N j(ref_q[4],m[0],m[1],m[4]);
  adapted__udp_mux_2to1_N k(dut_q[4],m[0],m[1],m[4]);
  sky130_fd_sc_hd__udp_mux_4to2 l(ref_q[5],m[0],m[1],m[2],m[3],m[4],m[5]);
  adapted__udp_mux_4to2 n(dut_q[5],m[0],m[1],m[2],m[3],m[4],m[5]);
  task check;
    #1; if (ref_q !== dut_q) $fatal(1,"UDP mismatch ref=%b dut=%b",ref_q,dut_q);
  endtask
  initial begin
    #1; control=1; check(); control=0; check();
    // Exhaust every initial state, next input and both stored values. Pin
    // transitions are separated, avoiding undefined simultaneous UDP events.
    for (integer seed=0;seed<2;seed=seed+1)
      for (integer s=0;s<8;s=s+1)
        for (integer t=0;t<8;t=t+1) begin
          clk=0; check(); d=seed; check(); clk=1; check();
          d=s[0]; check(); clk=s[1]; check(); control=s[2]; check();
          d=t[0]; check(); clk=t[1]; check(); control=t[2]; check();
        end
    for (integer x=0;x<64;x=x+1) begin m=x; check(); end
    $display("UDP_EQUIVALENCE_PASS"); $finish;
  end
endmodule
""")
    binary = tmp_path / "sim"
    subprocess.run(["iverilog", "-g2012", "-s", "tb", "-o", str(binary),
                    str(source), str(adapted), str(tb)], check=True, capture_output=True)
    result = subprocess.run(["vvp", str(binary)], check=True, capture_output=True, text=True)
    assert "UDP_EQUIVALENCE_PASS" in result.stdout
