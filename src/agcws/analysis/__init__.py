"""Analysis helpers for preregistered experiment outputs."""

from .aggregate import aggregate_summaries, bootstrap_mean_ci
from .inference import holm_bonferroni, paired_permutation_pvalue, rank_biserial_effect
from .metrics import best_so_far_auc, evaluations_to_target, summarize_run
from .rank_agreement import rank_agreement

__all__ = ["aggregate_summaries", "bootstrap_mean_ci", "holm_bonferroni",
           "paired_permutation_pvalue", "rank_biserial_effect", "best_so_far_auc", "evaluations_to_target",
           "rank_agreement", "summarize_run"]
