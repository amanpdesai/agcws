"""Presentation changes preserve bin data and keep figure text inside the PDF."""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg

SPEC = importlib.util.spec_from_file_location("paper_build", Path("paper/scripts/build.py"))
paper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(paper)


@pytest.mark.parametrize('extra_policy', [False, True])
def test_waveform_steps_annotations_and_label_bounds(tmp_path, monkeypatch, extra_policy):
    recipe = json.loads((paper.PAPER / "evidence/figure_recipe.json").read_text())
    evidence = json.loads((paper.PAPER / "evidence/mesh_examples.json").read_text())
    if extra_policy:
        recipe['sources']['Strong'] = {'arm': 'strong-medium-64k'}
        for case in evidence['cases']:
            # Synthetic layout fixture only, never published as a measurement.
            case['arms']['Strong'] = {**case['arms']['Flash-Lite'], 'model': 'gemini-3.8-flash'}
        (tmp_path / 'evidence').mkdir()
        (tmp_path / 'evidence/mesh_examples.json').write_text(json.dumps(evidence))
        (tmp_path / 'evidence/figure_recipe.json').write_text(json.dumps(recipe))
        monkeypatch.setattr(paper, 'PAPER', tmp_path)
    saved = []
    monkeypatch.setattr(paper.plt.Figure, "savefig", lambda fig, *a, **k: saved.append(fig))
    paper.render_waveforms(tmp_path)
    fig = saved[0]
    FigureCanvasAgg(fig)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for panel, (ax, case) in enumerate(zip(fig.axes, evidence["cases"], strict=True)):
        ordered = [(label, case["arms"][label]) for label in recipe["display_order"]
                   if label in case["arms"]]
        for patch, (label, row) in zip(ax.patches[1:], ordered, strict=True):
            np.testing.assert_allclose(patch.get_data().values,
                                       np.asarray(row["rates"]) / evidence["scale"])
            style = paper.POLICY_STYLES[recipe["sources"][label]["arm"]]
            assert patch.get_linestyle() == style["linestyle"]
        annotation = fig.texts[panel].get_text()
        assert annotation.splitlines() == [
            f"{label}: {case['arms'][label]['charged_slots']} charged proposals"
            for label in recipe['annotation_policies']
        ]
        for artist in [ax.xaxis.label, ax.yaxis.label, ax.title, *ax.texts]:
            bounds = artist.get_window_extent(renderer)
            assert bounds.x0 >= 0 and bounds.y0 >= 0
            assert bounds.x1 <= fig.bbox.width and bounds.y1 <= fig.bbox.height
    legend = fig.legends[0].get_window_extent(renderer)
    assert legend.x0 >= 0 and legend.x1 <= fig.bbox.width and legend.y0 >= 0
    for artist in fig.texts:
        bounds = artist.get_window_extent(renderer)
        assert bounds.y0 > legend.y1
        assert bounds.x0 >= 0 and bounds.x1 <= fig.bbox.width
        for ax in fig.axes:
            assert bounds.y1 < ax.xaxis.label.get_window_extent(renderer).y0


def test_pending_cells_are_detected_without_todos(tmp_path):
    (tmp_path / "table.tex").write_text(r"AES & \pending & \pending \\")
    assert paper.pending_table_cells(tmp_path) == 2


@pytest.mark.parametrize("policies", [[], ["Missing"], ["Flash-Lite", "Flash-Lite"]])
def test_waveform_rejects_invalid_annotation_policies(tmp_path, monkeypatch, policies):
    recipe = json.loads((paper.PAPER / "evidence/figure_recipe.json").read_text())
    evidence = (paper.PAPER / "evidence/mesh_examples.json").read_text()
    recipe["annotation_policies"] = policies
    (tmp_path / "evidence").mkdir()
    (tmp_path / "evidence/mesh_examples.json").write_text(evidence)
    (tmp_path / "evidence/figure_recipe.json").write_text(json.dumps(recipe))
    monkeypatch.setattr(paper, "PAPER", tmp_path)
    with pytest.raises(ValueError, match="presentation settings"):
        paper.render_waveforms(tmp_path)


def test_architecture_simulation_label(tmp_path, monkeypatch):
    saved = []
    monkeypatch.setattr(paper.plt.Figure, "savefig", lambda fig, *a, **k: saved.append(fig))
    paper.render_system(tmp_path)
    labels = [artist.get_text() for artist in saved[0].axes[0].texts]
    assert "RTL\nSimulation" in labels
    assert "RTL\nexecution" not in labels
