import re
from pathlib import Path


def test_only_one_active_results_document():
    assert Path("RESULTS.md").is_file()
    assert not list(Path("docs").glob("*RESULTS.md"))
    assert not list(Path("experiments").rglob("*.py"))


def test_active_documentation_links_resolve():
    files = [
        Path("README.md"),
        Path("RESULTS.md"),
        Path("CONTRIBUTING.md"),
        *Path("docs").glob("*.md"),
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
    for target in ("test:", "lint:", "archive-check:", "archive-audit:", "pipeline-help:"):
        assert target in text
    assert "P_MIN" not in text and "P_MAX" not in text
    assert "run_aes_search.py" not in text and "launch_nonflat" not in text
