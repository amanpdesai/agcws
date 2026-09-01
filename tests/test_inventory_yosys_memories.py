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
