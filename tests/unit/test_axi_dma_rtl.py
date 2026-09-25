import subprocess
from pathlib import Path

from agcws.core import config


def test_pinned_axi_dma_rtl_compiles(tmp_path: Path):
    result = subprocess.run(
        [config.IVERILOG, "-g2012", "-s", "axi_dma", "-o", str(tmp_path / "axi_dma.vvp"),
         *[f"benchmarks/verilog-axi/rtl/{name}.v" for name in
           ("axi_dma", "axi_dma_rd", "axi_dma_wr", "axi_dma_desc_mux")]],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "axi_dma.vvp").is_file()
