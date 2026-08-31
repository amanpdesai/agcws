from pathlib import Path
import subprocess


def test_axi_dma_write_smoke_completes(tmp_path: Path):
    result = subprocess.run(
        ["bash", "scripts/run_axi_dma_wr_smoke.sh", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "AGCWS_AXI_DMA_WR_OK beats=16" in result.stdout
    assert (tmp_path / "activity.vcd").is_file()
