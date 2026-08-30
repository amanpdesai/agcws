from dataclasses import dataclass, field
from typing import Any, Callable
from agcws.goals import Goal
from agcws.policies import SearchPolicy
from agcws.adapters import DesignAdapter
from agcws.nodes.validation import validate_workload

@dataclass
class LoopState:
    goal: Goal
    policy: SearchPolicy
    history: list[Any] = field(default_factory=list)
    proposal_index: int = 0

def propose_batch(state: LoopState, adapter: DesignAdapter, batch_size: int) -> list[dict]:
    """Persistent agent state: shell tasks return results; history stays here."""
    candidates = state.policy.propose(adapter, state.goal, state.history, batch_size)
    state.proposal_index += len(candidates)
    return candidates

def validate_batch(adapter: DesignAdapter, candidates: list[dict]) -> list[tuple[dict, Any]]:
    return [(candidate, validate_workload(adapter, candidate)) for candidate in candidates]
