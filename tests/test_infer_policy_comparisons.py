import json

from scripts.infer_policy_comparisons import main


def test_infer_policy_comparisons_pairs_seeds(tmp_path, monkeypatch):
    for seed in (0, 1):
        for policy, auc in (("random", 5.0 + seed), ("mutation", 3.0 + seed)):
            root = tmp_path / f"seed{seed}" / policy
            root.mkdir(parents=True)
            (root / "summary.json").write_text(json.dumps({
                "policy": policy, "design": "demo", "target": "0.5",
                "seed": seed, "auc_best_so_far": auc,
                "evaluations_to_target": 2, "solved": True,
            }))
    out = tmp_path / "inference.json"
    monkeypatch.setattr("sys.argv", ["infer", str(tmp_path / "seed0"),
                                      str(tmp_path / "seed1"), "--out", str(out)])
    main()
    result = json.loads(out.read_text())
    assert result["comparisons"][0]["pairs"] == 2
