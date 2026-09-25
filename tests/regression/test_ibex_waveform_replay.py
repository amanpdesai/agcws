import pytest

from agcws.evidence.replay import normalized


def test_date_only_is_normalized_not_signal_changes():
    def trace(date, value):
        return iter(f"$date\n{date}\n$end\n$enddefinitions $end\n#0\n{value}!\n".splitlines(True))
    a, b, c = normalized(trace("old", 0)), normalized(trace("new", 0)), normalized(trace("new", 1))
    assert a["semantic_stream_sha256"] == b["semantic_stream_sha256"]
    assert a["date_metadata"] != b["date_metadata"]
    assert a["semantic_stream_sha256"] != c["semantic_stream_sha256"]
    with pytest.raises(ValueError, match="incomplete"):
        normalized(iter(["$date\n"]))
