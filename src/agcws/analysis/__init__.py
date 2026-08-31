"""Analysis helpers for preregistered experiment outputs."""

from .rank_agreement import rank_agreement
from .metrics import best_so_far_auc, evaluations_to_target, summarize_run
from .aggregate import aggregate_summaries, bootstrap_mean_ci

__all__ = ["aggregate_summaries", "bootstrap_mean_ci", "best_so_far_auc", "evaluations_to_target",
           "rank_agreement", "summarize_run"]
