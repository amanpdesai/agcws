from pathlib import Path


def test_cross_pdk_script_propagates_frontend_configuration():
    text = Path("scripts/run_aes_cross_pdk.sh").read_text()
    assert 'AGCWS_SLANG_PLUGIN="${AGCWS_SLANG_PLUGIN:-}"' in text
    assert 'waveform_path.is_file()' in text
