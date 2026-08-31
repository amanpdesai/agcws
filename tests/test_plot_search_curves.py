import json
from pathlib import Path

from analysis.plot_search_curves import load_curves, mean_curves


def test_load_and_mean_search_curves(tmp_path: Path):
    run = tmp_path / "random" / "seed-0"
    run.mkdir(parents=True)
    (run / "summary.json").write_text(json.dumps({"policy": "random"}))
    (run / "best_so_far.json").write_text(json.dumps({"error": [1, 0.5]}))
    curves = load_curves(tmp_path)
    assert curves == {"random": [[1.0, 0.5]]}
    assert mean_curves(curves) == {"random": [1.0, 0.5]}


def test_load_search_curves_merges_multiple_roots(tmp_path: Path):
    roots = []
    for seed, curve in ((0, [1, 0.5]), (1, [1, 0.25])):
        root = tmp_path / f"root-{seed}" / "random" / f"seed-{seed}"
        root.mkdir(parents=True)
        (root / "summary.json").write_text(json.dumps({"policy": "random"}))
        (root / "best_so_far.json").write_text(json.dumps({"error": curve}))
        roots.append(root.parents[1])
    curves = load_curves(roots)
    assert curves == {"random": [[1.0, 0.5], [1.0, 0.25]]}
