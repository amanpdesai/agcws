import pytest

from agcws.designs.assets import asset_path


@pytest.mark.parametrize("design,name", [
    ("aes", "rtl.sv"), ("aes", "gls.sv"), ("aes", "transactions.svh"),
    ("dma", "axi_dma_coupled_tb.py"), ("dma", "axi_dma_pipelined_tb.py"),
    ("mesh", "mesh_temporal.sv"), ("redmule", "redmule_temporal.c"),
])
def test_assets_do_not_depend_on_working_directory(tmp_path, monkeypatch, design, name):
    monkeypatch.chdir(tmp_path)
    path = asset_path(design, name)
    assert path.is_absolute() and path.is_file()


@pytest.mark.parametrize("design,name", [("../aes", "rtl.sv"), ("aes", "../rtl.sv"),
                                         ("aes", ".."), ("aes", "")])
def test_asset_paths_cannot_escape_owner(design, name):
    with pytest.raises(ValueError):
        asset_path(design, name)
