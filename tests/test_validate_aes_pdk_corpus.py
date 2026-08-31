import json

from scripts.validate_aes_pdk_corpus import validate


def _report(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"Total                0 0 0 {value} 100.0%\n")


def test_validate_aes_pdk_corpus_requires_and_pairs_reports(tmp_path):
    corpus = tmp_path / "corpus"
    for index in range(2):
        trial = corpus / f"trial-{index:04d}"
        trial.mkdir(parents=True)
        (trial / "workload.json").write_text(json.dumps({"ops": [index]}))
    sky = tmp_path / "sky"
    nangate = tmp_path / "nangate"
    _report(sky / "trial-0000" / "power.rpt", "2.0")
    _report(sky / "trial-0001" / "power.rpt", "3.0")
    _report(nangate / "trial-0000" / "power.rpt", "1.0")
    _report(nangate / "trial-0001" / "power.rpt", "1.5")

    result = validate(corpus, sky, nangate, tmp_path / "result.json")

    assert result["workloads"] == 2
    assert result["rank_agreement"]["shared_workloads"] == 2
    assert json.loads((tmp_path / "result.json").read_text())["pdks"]["sky130hd"]["min_w"] == 2.0
