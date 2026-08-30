from dataclasses import dataclass, field
from typing import Any, Callable
from agcws.goals import Goal
from agcws.policies import SearchPolicy
from agcws.adapters import DesignAdapter
from agcws.nodes.validation import validate_static

@dataclass
class LoopState:
    goal: Goal
    policy: SearchPolicy
    history: list[Any] = field(default_factory=list)
    proposal_index: int = 0
    budget: int = 200

def propose_batch(state: LoopState, adapter: DesignAdapter, batch_size: int) -> list[dict]:
    """Persistent agent state: shell tasks return results; history stays here."""
    remaining = state.budget - state.proposal_index
    if remaining <= 0:
        return []
    requested = min(batch_size, remaining)
    candidates = state.policy.propose(adapter, state.goal, state.history, requested)
    # The requested slots are consumed even when parsing/validation returns fewer.
    state.proposal_index += requested
    return candidates

def validate_batch(adapter: DesignAdapter, candidates: list[dict]) -> list[tuple[dict, Any]]:
    return [(candidate, validate_static(adapter, candidate)) for candidate in candidates]
