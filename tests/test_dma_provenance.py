import importlib.util
from pathlib import Path


def _runner_module():
    path = Path("scripts/run_axi_dma_workload.py").resolve()
    spec = importlib.util.spec_from_file_location("run_axi_dma_workload", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_rtl_provenance_hashes_copied_tree(tmp_path: Path):
    rtl = tmp_path / "rtl"
    rtl.mkdir()
    (rtl / "axi_dma.v").write_text("module axi_dma; endmodule\n")
    tree = tmp_path / "verilog-axi"
    tree.mkdir()
    (tree / "rtl").symlink_to(rtl, target_is_directory=True)

    provenance = _runner_module().rtl_provenance(tree)

    assert provenance["rtl_identity"] == "copied_tree"
    assert len(provenance["rtl_tree_sha256"]) == 64
