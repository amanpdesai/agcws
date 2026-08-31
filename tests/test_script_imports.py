from pathlib import Path


def test_direct_evaluation_script_bootstraps_src_path():
    text = Path("scripts/evaluate_aes_workload.py").read_text()
    assert 'sys.path.insert(0, str(ROOT / "src"))' in text
