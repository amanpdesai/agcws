from pathlib import Path

from scripts.write_aes_pdk_manifest import digest, write


def test_aes_pdk_corpus_runner_is_fail_closed():
    text = Path("scripts/run_aes_pdk_corpus.sh").read_text()
    assert "at least two trial workloads" in text
    assert "missing waveform" in text
    assert "validate_aes_pdk_corpus.py" in text
    assert "write_aes_pdk_manifest.py" in text
    assert "run-manifest.json" in text


def test_pdk_manifest_records_all_input_digests(tmp_path: Path, monkeypatch):
    corpus = tmp_path / "corpus" / "trial-0000"
    corpus.mkdir(parents=True)
    (corpus / "workload.json").write_text('{"operations": []}\n')
    (corpus / "activity.vcd").write_text("vcd\n")
    synth_dirs = []
    for name in ("sky", "nangate"):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "mapped.v").write_text("module top; endmodule\n")
        (directory / "manifest.json").write_text('{"top": "top"}\n')
        synth_dirs.append(directory)
    sky_lib = tmp_path / "sky.lib"
    nangate_lib = tmp_path / "nangate.lib"
    sky_lib.write_text("sky\n")
    nangate_lib.write_text("nangate\n")
    monkeypatch.setattr("scripts.write_aes_pdk_manifest.version", lambda *args: "test-tool")

    output = tmp_path / "run-manifest.json"
    result = write(output, corpus.parent, synth_dirs[0], synth_dirs[1], sky_lib, nangate_lib)
    assert result["workloads"] == 1
    assert result["workload_sha256"] == [digest(corpus / "workload.json")]
    assert result["waveform_sha256"] == [digest(corpus / "activity.vcd")]
    assert result["tools"] == {"opensta": "test-tool", "yosys": "test-tool"}
    assert result["synthesis"]["sky130hd"]["netlist_sha256"] == digest(synth_dirs[0] / "mapped.v")
    assert result["synthesis"]["nangate45"]["liberty_sha256"] == digest(nangate_lib)
