from agcws.adapters.aes import AESAdapter
from agcws.adapters.base import ValidityStage
from agcws.nodes.validation import validate_workload

def test_aes_protocol_requires_configuration():
    result = validate_workload(AESAdapter(), {"operations": [{"op": "encrypt"}]})
    assert result.stage is ValidityStage.PROTOCOL

def test_aes_accepts_configured_workload():
    result = validate_workload(AESAdapter(), {"operations": [{"op": "configure"}, {"op": "encrypt"}]})
    assert result.valid
