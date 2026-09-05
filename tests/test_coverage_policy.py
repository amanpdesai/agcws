from types import SimpleNamespace

import pytest

from agcws.adapters.aes.transactions import AESTransactionAdapter
from agcws.adapters.base import Validity, ValidityStage
from agcws.policies.coverage_guided import CoverageGuidedSearch


def test_coverage_policy_refuses_uninstrumented_valid_history():
    trial = SimpleNamespace(validity=Validity(True), profile=SimpleNamespace(provenance={}))
    with pytest.raises(ValueError, match='instrumented'):
        CoverageGuidedSearch().propose(AESTransactionAdapter(), None, [trial], 4)


def test_invalid_trials_cannot_seed_coverage_queue():
    trial = SimpleNamespace(validity=Validity(False, ValidityStage.FUNCTIONAL, 'bad'),
                            profile=SimpleNamespace(provenance={'coverage_hits': ['fake']}))
    left = CoverageGuidedSearch(17).propose(AESTransactionAdapter(), None, [trial], 4)
    right = CoverageGuidedSearch(17).propose(AESTransactionAdapter(), None, [], 4)
    assert left == right
