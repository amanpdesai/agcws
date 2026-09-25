import json
import re
from pathlib import Path


def test_only_one_active_results_document():
    assert Path("docs/RESULTS.md").is_file()
    assert not Path("RESULTS.md").exists()
    assert not list(Path("experiments").rglob("*.py"))


def test_paper_layout_separates_source_evidence_and_generated_assets():
    paper = Path('paper')
    assert not list(paper.glob('*.py'))
    assert not list(paper.glob('*.json'))
    assert not list(paper.glob('window_*'))
    assert not (paper / 'evidence/strong_mesh_snapshot').exists()
    for name in ('build', 'extract', 'extract_strong', 'extract_power', 'overleaf'):
        assert (paper / 'scripts' / f'{name}.py').is_file()
    for name in ('figure_recipe.json', 'build_provenance.json', 'mesh_examples.json'):
        assert (paper / 'evidence' / name).is_file()
    for name in ('matched_curves.pdf', 'matched_table.tex', 'flash_efficiency.tex',
                 'mesh_power_profiles.pdf'):
        assert (paper / 'figures/supplementary' / name).is_file()
        assert not (paper / 'figures' / name).exists()


def test_smoke_inputs_live_with_their_consumers():
    from importlib.resources import files

    assert Path('benchmarks/README.md').is_file()
    assert not Path('third_party').exists()
    assert Path('src/agcws/baselines/phase.py').is_file()
    assert Path('src/agcws/search/dispatch.py').is_file()
    assert Path('tests/fixtures/study_example.json').is_file()
    assert files('agcws.designs.dma').joinpath('assets/smoke.json').is_file()


def test_evaluation_ownership_and_retired_helpers():
    root = Path('src/agcws')
    assert not (root / 'evaluation/tools').exists()
    assert not (root / 'designs/dma/harnesses').exists()
    assert (root / 'evaluation/activity/known_bits.py').is_file()
    assert (root / 'evaluation/activity/generic.py').is_file()
    assert (root / 'designs/temporal_registry.py').is_file()
    assert not list((root / 'evidence/frozen_runs').glob('*.py'))
    assert not (root / 'evidence/container_inputs.py').exists()
    assert not (root / 'evidence/strong_resume.py').exists()


def test_curve_summaries_do_not_replace_trial_metrics():
    from agcws.reporting.metrics import summarize
    from agcws.reporting.statistics.curves import best_so_far_auc

    errors = [1.0, 0.5, 0.8]
    trials = [dict(slot=i, valid=True, loss=value)
              for i, value in enumerate(errors, 1)]
    result = summarize(trials, 3, 0.05)
    assert result['curve'] == [1.0, 0.5, 0.5]
    assert result['auc'] == best_so_far_auc(result['curve'])
    assert result['auc'] != best_so_far_auc(errors)


def test_current_evidence_index_resolves_and_records_completed_state():
    index = json.loads(Path("results/index.json").read_text())
    assert index['version'] == 2
    assert set(index['designs']) == {'aes', 'dma', 'ibex', 'mesh', 'redmule'}
    for path in index['summaries'].values():
        assert Path(path).is_file()
    for row in index['designs'].values():
        for path in row.values():
            assert Path(path).exists()
    assert json.loads(Path(index['summaries']['gemini_3_8']).read_text())['designs']['aes']['nonflat']['solved'] == 80


def test_active_documentation_links_resolve():
    files = [
        Path("README.md"),
        *Path("docs").rglob("*.md"),
        *Path("results").glob("*/README.md"),
    ]
    for path in files:
        for url in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
            url = url.split("#")[0]
            if not url or url.startswith(("http", "mailto:", "/")):
                continue
            assert (path.parent / url).exists(), (path, url)


def test_research_commands_are_explicit_and_have_no_stale_envelope():
    text = Path("Makefile").read_text()
    for target in ("test:", "lint:", "doctor:", "container-smoke:", "help:"):
        assert target in text
    assert "P_MIN" not in text and "P_MAX" not in text
    assert "run_aes_search.py" not in text and "launch_nonflat" not in text
