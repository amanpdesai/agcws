import json

import pytest

from agcws.evaluation.power.finalists import run
from agcws.reporting.metrics import error, key, max_bin_error
from agcws.studies.finalists import select, verify


def fixture(tmp_path, domain="aes-temporal"):
    root = tmp_path / "study"
    cell = root / "panel/t/1/random"
    batch = cell / "batches/001"
    batch.mkdir(parents=True)
    manifest = {"spec": {"domain": domain, "targets": {"t": [1] * 8},
                         "scale": 1, "seeds": [1], "policies": ["random"],
                         "budget": 2, "tolerance": .05, "stop_on_success": True,
                         "success_metric": "max-bin"}, "measurement_fingerprint": "frozen"}
    (root / "manifest.json").write_text(json.dumps(manifest))
    trials = [{"slot": i, "valid": True, "rates": [v] * 8, "loss": abs(1-v),
               "max_bin_error": abs(1-v), "canonical_program": {"sequence": [i]}}
              for i, v in [(1, .5), (2, .75)]]
    path = batch / "trials.json"
    path.write_text(json.dumps(trials))
    (cell / "complete.json").write_text("{}")
    return root, path


def test_selection_keeps_unsolved_best_and_verifies(tmp_path):
    root, path = fixture(tmp_path)
    plan = select([root])
    assert plan["cases"][0]["slot"] == 2
    assert not plan["cases"][0]["activity_solved"]
    verify(plan)
    path.write_text("[]")
    with pytest.raises(ValueError, match="input changed"):
        verify(plan)


def test_incomplete_is_explicit(tmp_path):
    root, _ = fixture(tmp_path)
    (root / "panel/t/1/random/complete.json").unlink()
    with pytest.raises(ValueError, match="incomplete"):
        select([root])
    plan = select([root], True)
    assert not plan["cases"]
    assert plan["omitted"][0]["reason"] == "incomplete"


def test_duplicate_roots_rejected(tmp_path):
    root, _ = fixture(tmp_path)
    with pytest.raises(ValueError, match="duplicate"):
        select([root, root])


def test_forged_score_rejected(tmp_path):
    root, path = fixture(tmp_path)
    trials = json.loads(path.read_text())
    trials[0]["loss"] = 0
    path.write_text(json.dumps(trials))
    with pytest.raises(ValueError, match="metrics differ"):
        select([root])


def test_declared_synthesis_source_root_is_verified(tmp_path):
    from agcws.evaluation.power.finalists import sha, verify_synthesis_sources
    source = tmp_path / 'core.sv'
    source.write_text('module core; endmodule')
    manifest = {'source_root': str(tmp_path), 'sources': {'core.sv': sha(source)}}
    verify_synthesis_sources(manifest)
    source.write_text('changed')
    with pytest.raises(ValueError, match='source differs'):
        verify_synthesis_sources(manifest)
    with pytest.raises(ValueError, match='unsafe'):
        verify_synthesis_sources({'source_root': str(tmp_path), 'sources': {'../core.sv': 'bad'}})


def test_unsupported_does_not_run_or_create_output(tmp_path):
    root, _ = fixture(tmp_path, "unsupported-temporal")
    plan = select([root])
    with pytest.raises(NotImplementedError, match="no validated"):
        run(plan, plan["cases"][0]["id"], tmp_path, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_plan_tampering_rejected(tmp_path):
    root, _ = fixture(tmp_path)
    plan = select([root])
    plan["cases"][0]["slot"] = 1
    with pytest.raises(ValueError, match="plan changed"):
        verify(plan)


def test_changed_source_rejected_before_execution(tmp_path):
    root, _ = fixture(tmp_path)
    path = root / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["sources"] = {str(path): "wrong"}
    path.write_text(json.dumps(manifest))
    plan = select([root])
    with pytest.raises(ValueError, match="frozen source checkout"):
        run(plan, plan["cases"][0]["id"], tmp_path, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_plan_checksum_covers_omissions(tmp_path):
    root, _ = fixture(tmp_path)
    plan = select([root])
    assert plan["sha256"] == key({k: v for k, v in plan.items() if k != "sha256"})


def test_declared_max_bin_gate_controls_selection_not_average(tmp_path):
    root, path = fixture(tmp_path)
    trials = json.loads(path.read_text())
    for trial, rates in zip(trials, [[1.2] * 8, [1.4] + [1] * 7]):
        trial.update(rates=rates, loss=error(rates, [1] * 8, 1),
                     max_bin_error=max_bin_error(rates, [1] * 8, 1))
    path.write_text(json.dumps(trials))
    assert trials[1]["loss"] < trials[0]["loss"]
    assert select([root])["cases"][0]["slot"] == 1


def test_report_missing_power_is_not_zero(tmp_path):
    from agcws.reporting.finalists import collect, export

    root, _ = fixture(tmp_path)
    report = collect(select([root]), [])
    assert report["cases"][0]["power_w"] is None
    assert report["cases"][0]["power_status"] == "not_measured"
    assert report["cases"][0]["signed_residual"] == [-.25] * 8
    export(report, tmp_path / "report")
    assert len((tmp_path / "report/bins.csv").read_text().splitlines()) == 9
    assert len(list((tmp_path / "report/workloads").glob("*.json"))) == 1


def test_paper_recipe_verifies_inputs_and_records_explicit_selection(tmp_path, monkeypatch):
    from agcws.reporting import paper

    root, _ = fixture(tmp_path)
    plan = select([root])
    (tmp_path / "plan.json").write_text(json.dumps(plan))
    recipe = tmp_path / "recipe.json"
    recipe.write_text(json.dumps({"version": 1, "plan": "plan.json",
                                  "measurements": [], "cases": [plan["cases"][0]["id"]]}))
    seen = []

    def plot(case, path):
        seen.append(case)
        path.write_bytes(b"figure fixture")

    monkeypatch.setattr(paper, "plot", plot)
    receipt = paper.render(recipe, tmp_path / "figures")
    assert receipt["plan_sha256"] == plan["sha256"]
    assert receipt["figures"][0]["power_status"] == "not_measured"
    assert seen[0]["power_w"] is None
    assert (tmp_path / "figures/provenance.json").is_file()
    with pytest.raises(FileExistsError):
        paper.render(recipe, tmp_path / "figures")
    plan["cases"][0]["rates"][0] += 1
    (tmp_path / "plan.json").write_text(json.dumps(plan))
    with pytest.raises(ValueError):
        paper.render(recipe, tmp_path / "tampered")
    assert not (tmp_path / "tampered").exists()


def test_report_rejects_other_selection_and_tampering(tmp_path):
    from agcws.designs.aes.gls import sha
    from agcws.reporting.finalists import collect

    root, _ = fixture(tmp_path)
    plan = select([root])
    directory = tmp_path / "power"
    directory.mkdir()
    measurement = directory / "measurement.json"
    result = {"case_id": plan["cases"][0]["id"], "plan_sha256": "wrong"}
    measurement.write_text(json.dumps(result))
    (directory / "complete.json").write_text(json.dumps({"measurement_sha256": sha(measurement)}))
    with pytest.raises(ValueError, match="another selection"):
        collect(plan, [directory])
    measurement.write_text("{}")
    with pytest.raises(ValueError, match="checkpoint changed"):
        collect(plan, [directory])


@pytest.mark.parametrize("domain,declared", [
    ("aes-temporal", None), ("dma-temporal", None), ("ibex-temporal", None),
    ("ibex-temporal", "slew-verified-v1"), ("ibex-temporal", "strict")])
@pytest.mark.parametrize("annotated", [100, 90])
def test_replay_wiring_and_lossless_retirement(tmp_path, monkeypatch, domain, declared, annotated):
    from types import SimpleNamespace

    import agcws.evaluation.power.finalists as runner
    from agcws.designs.aes.gls import sha

    root, _ = fixture(tmp_path, domain)
    manifest = json.loads((root / "manifest.json").read_text())
    source = tmp_path / 'source.py'
    source.write_text('measurement source')
    manifest["sources"] = {'source.py': sha(source)}
    monkeypatch.setattr(runner.config, 'ROOT', tmp_path)
    (root / "manifest.json").write_text(json.dumps(manifest))
    plan = select([root])
    if declared is not None:
        plan['cases'][0]['reconstruction_policy'] = declared
        plan['sha256'] = key({k: v for k, v in plan.items() if k != 'sha256'})
    synthesis = tmp_path / "synthesis"
    synthesis.mkdir()
    mapped = synthesis / "mapped.v"
    mapped.write_text("module fixture; endmodule")
    liberty = tmp_path / "cells.lib"
    liberty.write_text("fixture")
    (synthesis / "manifest.json").write_text(json.dumps({
        "sources": {str(mapped): sha(mapped)}, "netlist_sha256": sha(mapped),
        "liberty_sha256": sha(liberty)}))
    monkeypatch.setattr(runner.config, "LIBERTY", liberty)
    for name in ("AGCWS_SKY130_CELL_MODELS", "AGCWS_SKY130_PRIMITIVES"):
        monkeypatch.setenv(name, str(mapped))

    def measured(program, scratch, manifest):
        attempt = scratch / 'cache/key' / ('run' if domain == 'ibex-temporal' else 'attempt-001')
        attempt.mkdir(parents=True)
        (attempt / "activity.vcd").write_text("fixture waveform")
        return {"valid": True, "rates": [.75] * 8, "cache_id": "key",
                "profile": {"timescale": "1ps", "period_ticks": 10000}}, False

    monkeypatch.setattr(runner, "backend", lambda _: SimpleNamespace(measured=measured, clock_edges=80))
    monkeypatch.setattr(runner, 'replay_frozen',
                        lambda case, manifest, runtime, scratch:
                        measured(case['program'], scratch, manifest)[0])
    commands, retired = [], []

    def tool(command, **kwargs):
        commands.append(command)
        gls = tmp_path / "output/gls"
        gls.mkdir()
        (gls / "activity.vcd").write_text("fixture gates")

    monkeypatch.setattr(runner.subprocess, "run", tool)
    if domain == 'ibex-temporal':
        def replay_trial(rtl, synthesis, gls, **kwargs):
            gls.mkdir()
            waveform = gls / 'activity.vcd'
            waveform.write_text('fixture gates')
            return {'rtl_waveform': str(rtl / 'activity.vcd'), 'waveform': str(waveform),
                    'clock': 'clk', 'scope': 'dut', 'clock_edges': 80, 'expected_period_s': 1e-8}
        monkeypatch.setattr(runner.importlib, 'import_module',
                            lambda name: SimpleNamespace(replay_trial=replay_trial))
    row = {"dynamic_power_w": .25, "annotated_pins": annotated, "unannotated_pins": 100-annotated}
    selected_options = []

    def evaluate(*args, **kwargs):
        selected_options.append(kwargs)
        return {'full': row, 'windows': [row]*8, 'grid': {'durations_s': [1e-6]*8}}

    monkeypatch.setattr(runner, 'evaluate', evaluate)

    def retire(path):
        assert (tmp_path / "output/measurement.json").is_file()
        retired.append(path)

    monkeypatch.setattr(runner, "compact", retire)
    if annotated < 99:
        with pytest.raises(ValueError, match="annotation coverage"):
            run(plan, plan["cases"][0]["id"], synthesis, tmp_path / "output")
        assert not (tmp_path / "output/complete.json").exists()
        assert not retired
        return
    result = run(plan, plan["cases"][0]["id"], synthesis, tmp_path / "output")
    assert len(retired) == 2
    assert result["gate_dynamic_energy_j"] == [2.5e-7] * 8
    assert (tmp_path / "output/complete.json").is_file()
    if domain == 'ibex-temporal':
        assert selected_options[0]['reconstruction_policy'] == (declared or 'strict')
        request = json.loads((tmp_path / 'output/request.json').read_text())
        assert request['plan_sha256'] == plan['sha256']
        assert request['reconstruction_policy'] == (declared or 'strict')
    else:
        assert commands[0][2] == ("agcws.designs.aes.gls" if domain == "aes-temporal" else "agcws.designs.dma.gls")


def test_reconstruction_policy_is_covered_by_frozen_plan_hash(tmp_path):
    root, _ = fixture(tmp_path, 'ibex-temporal')
    plan = select([root])
    old_hash = plan['sha256']
    plan['cases'][0]['reconstruction_policy'] = 'slew-verified-v1'
    with pytest.raises(ValueError, match='plan changed'):
        verify(plan)
    plan['sha256'] = key({k: v for k, v in plan.items() if k != 'sha256'})
    assert plan['sha256'] != old_hash
    verify(plan)


@pytest.mark.parametrize('domain,policy', [('aes-temporal', 'slew-verified-v1'),
                                        ('ibex-temporal', 'ibex-10ns-estimate-v1'),
                                        ('ibex-temporal', 'invented'), ('ibex-temporal', None)])
def test_invalid_explicit_policy_rejected_before_replay(tmp_path, domain, policy):
    root, _ = fixture(tmp_path, domain)
    plan = select([root])
    plan['cases'][0]['reconstruction_policy'] = policy
    plan['sha256'] = key({k: v for k, v in plan.items() if k != 'sha256'})
    with pytest.raises(ValueError, match='policy'):
        run(plan, plan['cases'][0]['id'], tmp_path, tmp_path / 'output')
    assert not (tmp_path / 'output').exists()


def test_redmule_proof_is_explicit_and_legacy_policy_cannot_run(tmp_path):
    from agcws.evaluation.power.finalists import reconstruction_policy
    from agcws.evaluation.power.windows import evaluate

    assert reconstruction_policy({'domain': 'redmule-temporal-long'}) == 'strict'
    assert reconstruction_policy({'domain': 'redmule-temporal-long',
                                  'reconstruction_policy': 'slew-verified-v1'}) == 'slew-verified-v1'
    with pytest.raises(ValueError, match='archival only'):
        evaluate(tmp_path, tmp_path, tmp_path, 'clk', 'dut', 8, tmp_path,
                 reconstruction_policy='ibex-10ns-estimate-v1')
