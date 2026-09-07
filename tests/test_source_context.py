import hashlib

import pytest

from agcws.policies.source_context import SourceReader, build_bundle


def reader(tmp_path, max_chars=100):
    source = tmp_path / "source"
    source.mkdir()
    (source / "rtl.sv").write_text("module test;\nendmodule\n")
    (source / "answer.json").write_text("secret witness")
    bundle = tmp_path / "bundle"
    build_bundle(source, bundle, ["rtl.sv"])
    digest = hashlib.sha256((bundle / "manifest.json").read_bytes()).hexdigest()
    return SourceReader(bundle, digest, max_chars)


def test_only_allowlisted_files_with_receipts(tmp_path):
    context = reader(tmp_path)
    result = context.read("rtl.sv", 1, 2)
    assert result["text"] == "1: module test;\n2: endmodule"
    assert context.receipts == [result["receipt"]]
    assert not (context.root / "answer.json").exists()
    for name in ("answer.json", "../answer.json", "/etc/passwd"):
        with pytest.raises(ValueError, match="allowlisted"):
            context.read(name, 1, 1)


def test_retrieval_limits_and_tampering(tmp_path):
    context = reader(tmp_path, 1)
    with pytest.raises(ValueError, match="budget"):
        context.read("rtl.sv", 1, 1)
    with pytest.raises(ValueError, match="exceeds"):
        context.read("rtl.sv", 1, 3)
    path = context.root / "rtl.sv"
    path.chmod(0o644)
    path.write_text("changed")
    with pytest.raises(ValueError, match="hash"):
        context.read("rtl.sv", 1, 1)


def test_bundle_rejects_escape_and_refuses_overwrite(tmp_path):
    context = reader(tmp_path)
    root = tmp_path / "source"
    (root / "escape").symlink_to(tmp_path / "bundle/rtl.sv")
    with pytest.raises(ValueError, match="escapes"):
        build_bundle(root, tmp_path / "bad", ["escape"])
    with pytest.raises(FileExistsError):
        build_bundle(root, context.root, ["rtl.sv"])
