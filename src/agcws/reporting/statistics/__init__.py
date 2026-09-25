"""Analysis helpers for preregistered experiment outputs."""

from agcws.reporting.statistics.aggregate import aggregate_summaries, bootstrap_mean_ci
from agcws.reporting.statistics.curves import best_so_far_auc, evaluations_to_target, summarize_run
from agcws.reporting.statistics.inference import (
           holm_bonferroni,
           paired_permutation_pvalue,
           rank_biserial_effect,
)
from agcws.reporting.statistics.rank_agreement import rank_agreement

__all__ = ["aggregate_summaries", "bootstrap_mean_ci", "holm_bonferroni",
           "paired_permutation_pvalue", "rank_biserial_effect", "best_so_far_auc", "evaluations_to_target",
           "rank_agreement", "summarize_run"]
