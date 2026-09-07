"""Deterministic peak-window niches shared by CPU and LLM structural search."""
import json
import math


def temporal_population(history, limit=8):
    if limit < 1:
        raise ValueError('population limit must be positive')
    eligible = []
    for trial in history:
        if not trial.validity.valid or trial.loss is None:
            continue
        rates = trial.profile.windowed if trial.profile else None
        if (not math.isfinite(trial.loss) or not rates
                or any(not math.isfinite(value) or value < 0 for value in rates)):
            raise ValueError('invalid measured population member')
        eligible.append(trial)
    eligible.sort(key=lambda trial: trial.loss)
    unique, seen = [], set()
    for trial in eligible:
        key = json.dumps(trial.workload, sort_keys=True, separators=(',', ':'))
        if key not in seen:
            seen.add(key)
            unique.append(trial)
    niches, selected = set(), []
    for trial in unique:
        rates = trial.profile.windowed
        peak = max(range(len(rates)), key=rates.__getitem__)
        if peak not in niches:
            niches.add(peak)
            selected.append(trial)
            if len(selected) == limit:
                return selected
    selected_ids = {id(trial) for trial in selected}
    selected.extend(trial for trial in unique if id(trial) not in selected_ids)
    return selected[:limit]
