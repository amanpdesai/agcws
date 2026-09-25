import json

from agcws.reporting.context import capacity


class Backend:
    def schema(self, n):
        assert n == 2
        return {}

    def payload(self, history, goal, n):
        assert [t["slot"] for t in history] == list(range(1, len(history)+1))
        return json.dumps(history)


def test_guard_applies_to_full_request_without_mutating_original():
    trial = {"slot": 99, "program": {"text": "x" * 2000}}
    rows = capacity(Backend(), trial, {})
    assert trial["slot"] == 99
    assert rows[0]["fits_current_200000_byte_guard"]
    assert not rows[-1]["fits_current_200000_byte_guard"]
    assert rows[-1]["guard_bytes"] == rows[-1]["payload_bytes"] + 2 + 4096
