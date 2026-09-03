from abc import ABC, abstractmethod
from typing import Any
from agcws.goals import Goal

class SearchPolicy(ABC):
    name: str
    claim_scope: str = "baseline"

    @abstractmethod
    def propose(self, adapter: Any, goal: Goal, history: list[Any], n: int) -> list[dict]:
        """Return n candidates in the adapter workload DSL."""
