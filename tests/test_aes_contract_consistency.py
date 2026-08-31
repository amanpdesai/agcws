from agcws.adapters.aes import AESAdapter
from agcws.adapters.base import SimResult, ValidityStage


def test_aes_floor_matches_frozen_calibration_decision():
    adapter = AESAdapter()
    assert adapter.useful_work_floor == 38
    result = adapter.validate_result(SimResult(True, True, True, 20))
    assert result.stage is ValidityStage.USEFUL_WORK


def test_aes_rejects_unsupported_key_length():
    result = AESAdapter().validate_protocol({"operations": [
        {"op": "configure", "key_len": 64},
    ]})
    assert result.stage is ValidityStage.PROTOCOL
