import pytest

from agcws.policies.profile import build_profile_policy


@pytest.mark.parametrize("name", [
    "random", "mutation", "evolutionary", "offline-agent", "one-shot-agent",
])
def test_profile_policy_factory_is_deterministic(name):
    left = build_profile_policy(name, 7)
    right = build_profile_policy(name, 7)
    assert left.name == right.name == name
    assert left.propose(None, None, [], 1) == right.propose(None, None, [], 1)


def test_profile_policy_factory_rejects_unknown_policy():
    with pytest.raises(ValueError, match="unknown profile policy"):
        build_profile_policy("not-a-policy")
