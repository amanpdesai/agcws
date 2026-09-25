import subprocess
from pathlib import Path

from agcws.core import config


def test_axi_dma_write_smoke_completes(tmp_path: Path):
    subprocess.run([config.IVERILOG, "-g2012", "-s", "agcws_axi_dma_wr_smoke",
                    "-o", str(tmp_path / "smoke.vvp"),
                    "src/agcws/designs/dma/assets/axi_dma_wr_smoke.v",
                    "benchmarks/verilog-axi/rtl/axi_dma_wr.v"], check=True)
    result = subprocess.run(
        [config.VVP, "smoke.vvp"], cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "AGCWS_AXI_DMA_WR_OK beats=16" in result.stdout
    assert (tmp_path / "activity.vcd").is_file()
