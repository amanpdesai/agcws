from pathlib import Path
import subprocess


def test_pinned_axi_dma_rtl_compiles(tmp_path: Path):
    result = subprocess.run(
        ["bash", "scripts/check_axi_dma_rtl.sh", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "axi_dma.vvp").is_file()
