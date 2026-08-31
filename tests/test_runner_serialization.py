from agcws.experiments.runner import _jsonable
from agcws.adapters.base import ValidityStage


def test_runner_serializes_nested_enums():
    assert _jsonable({"stage": ValidityStage.USEFUL_WORK}) == {"stage": "USEFUL_WORK"}
