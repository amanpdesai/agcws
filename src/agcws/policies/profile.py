"""Policy construction shared by profile-search entry points."""
from __future__ import annotations

from agcws.policies.agent import OfflineAgent, OneShotAgent
from agcws.policies.base import SearchPolicy
from agcws.policies.evolutionary import EvolutionarySearch
from agcws.policies.mutation import MutationSearch
from agcws.policies.random_search import RandomSearch


def build_profile_policy(name: str, seed: int = 0) -> SearchPolicy:
    """Build a deterministic policy for a profile run.

    Profile runners intentionally share the scalar policy vocabulary so that
    only the goal and evaluator change between arms.
    """
    policies = {
        "random": lambda: RandomSearch(seed),
        "mutation": lambda: MutationSearch(seed),
        "evolutionary": lambda: EvolutionarySearch(seed),
        "offline-agent": lambda: OfflineAgent(seed),
        "one-shot-agent": lambda: OneShotAgent(seed),
    }
    try:
        return policies[name]()
    except KeyError as exc:
        choices = ", ".join(sorted(policies))
        raise ValueError(f"unknown profile policy {name!r}; choose from {choices}") from exc
