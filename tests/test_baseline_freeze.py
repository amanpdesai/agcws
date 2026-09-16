import subprocess

import pytest

from scripts.prepare_baseline_matrix import committed_file


def test_commit_reader_follows_frozen_not_worktree_symlink(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "source.sv").write_text("original RTL")
    (tmp_path / "alias.sv").symlink_to("source.sv")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.org",
                    "commit", "-qm", "fixture"], cwd=tmp_path, check=True)
    (tmp_path / "source.sv").write_text("uncommitted RTL")
    assert committed_file(tmp_path, "HEAD", "alias.sv") == b"original RTL"
    with pytest.raises(ValueError, match="unsafe"):
        committed_file(tmp_path, "HEAD", "../outside")
