from pathlib import Path


def test_axi_dma_synthesis_script_uses_cached_netlist_contract():
    text = Path("scripts/synthesize_axi_dma.sh").read_text()
    assert "dfflibmap -liberty" in text
    assert "abc -liberty" in text
    assert '"top": "axi_dma"' in text


def test_axi_dma_opensta_script_uses_top_scope_and_clock():
    text = Path("scripts/run_opensta_axi_dma.sh").read_text()
    assert "link_design axi_dma" in text
    assert "-scope axi_dma" in text
    assert "get_ports clk" in text
    assert '"power_metric": "opensta_total_power_w"' in text
