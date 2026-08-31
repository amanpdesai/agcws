from agcws.adapters.aes import AESAdapter
from agcws.adapters.base import ValidityStage
from agcws.nodes.validation import validate_static, validate_workload
from agcws.adapters.base import SimResult

def test_aes_protocol_requires_configuration():
    result = validate_static(AESAdapter(), {"operations": [{"op": "encrypt"}]})
    assert result.stage is ValidityStage.PROTOCOL

def test_aes_accepts_configured_workload():
    result = validate_static(AESAdapter(), {"operations": [{"op": "configure"}, {"op": "encrypt"}]})
    assert result.valid

def test_useful_work_floor_is_hard_gate():
    result = validate_workload(AESAdapter(), {"operations": [{"op": "configure"}]}, SimResult(True, True, True, 1))
    assert not result.valid and result.stage is ValidityStage.USEFUL_WORK


def test_schema_rejects_unknown_fields_for_all_adapters():
    from agcws.adapters.axi_dma import AxiDmaAdapter
    from agcws.adapters.ibex import IbexAdapter
    assert validate_static(AESAdapter(), {"operations": [], "extra": 1}).stage is ValidityStage.SCHEMA
    assert validate_static(AxiDmaAdapter(), {"transfers": [], "extra": 1}).stage is ValidityStage.SCHEMA
    assert validate_static(IbexAdapter(), {"program": [{"op": "ecall"}], "extra": 1}).stage is ValidityStage.SCHEMA
