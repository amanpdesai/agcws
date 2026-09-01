import json
from pathlib import Path

from scripts.inventory_yosys_memories import inventory


def test_inventory_reports_memory_geometry(tmp_path: Path):
    source = tmp_path / "ram.sv"
    source.write_text("""
module ram(input logic clk, input logic we, input logic [2:0] addr,
           input logic [7:0] din, output logic [7:0] dout);
  logic [7:0] mem [0:7];
  always_ff @(posedge clk) begin
    if (we) mem[addr] <= din;
    dout <= mem[addr];
  end
endmodule
""")
    result = inventory("ram", [source], tmp_path / "inventory.json", yosys="yosys")
    assert result["memories"]
    memory = result["memories"][0]
    assert memory["width"] == 8
    assert memory["size"] == 8
    assert (tmp_path / "inventory.rtlil.json").is_file()
    assert json.loads((tmp_path / "inventory.json").read_text())["top"] == "ram"


def test_inventory_compat_frontend_converts_sources(tmp_path: Path):
    source = tmp_path / "cast_ram.sv"
    source.write_text("""
module cast_ram(input logic clk, input logic [1:0] addr,
                output logic [7:0] dout);
  logic [7:0] mem [0:3];
  always_ff @(posedge clk) dout <= mem[addr];
endmodule
""")
    result = inventory("cast_ram", [source], tmp_path / "inventory.json",
                       yosys="yosys", compat=True)
    assert result["compat"] is True
    assert (tmp_path / "frontend_compat/cast_ram.sv").is_file()
