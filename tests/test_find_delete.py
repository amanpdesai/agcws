import pytest

from maintenance.find_delete import execute_find


def test_find_deletes_only_exact_paths(tmp_path):
    selected = tmp_path / "selected trace.vcd"
    sibling = tmp_path / "keep.vcd"
    ledger = tmp_path / "trials.jsonl"
    for path in (selected, sibling, ledger):
        path.write_text("keep or delete by exact identity")
    result = execute_find(
        [selected], tmp_path / "journal.jsonl", tmp_path / "input.nul"
    )
    assert result == [str(selected)]
    assert not selected.exists()
    assert sibling.exists() and ledger.exists()


def test_find_handles_newlines_in_path(tmp_path):
    selected = tmp_path / "odd\nname.vcd"
    selected.write_text("trace")
    assert execute_find([selected], tmp_path / "journal", tmp_path / "input") == [
        str(selected)
    ]


def test_find_does_not_recurse_into_a_directory(tmp_path):
    directory = tmp_path / "directory"
    directory.mkdir()
    child = directory / "keep.vcd"
    child.write_text("do not traverse")
    with pytest.raises(RuntimeError, match="partial deletion"):
        execute_find([directory], tmp_path / "journal", tmp_path / "input")
    assert child.exists()


def test_find_does_not_follow_a_symlink(tmp_path):
    target = tmp_path / "keep.vcd"
    target.write_text("do not follow")
    link = tmp_path / "link.vcd"
    link.symlink_to(target)
    with pytest.raises(RuntimeError, match="partial deletion"):
        execute_find([link], tmp_path / "journal", tmp_path / "input")
    assert target.exists() and link.is_symlink()
