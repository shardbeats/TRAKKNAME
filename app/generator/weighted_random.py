"""Weighted random selection with zero-weight handling."""
from __future__ import annotations

import random


def _validate_weights(weights: list[float]) -> None:
    for w in weights:
        if w < 0:
            raise ValueError("Weights must be >= 0.")


def choose_weighted(items: list, weights: list[float], rng: random.Random | None = None):
    """Pick one item. Zero-weight items never selected; all-zero falls back to uniform."""
    rng = rng or random
    if not items:
        raise ValueError("No items to choose from.")
    _validate_weights(weights)
    if all(w <= 0 for w in weights):
        return rng.choice(items)
    return rng.choices(items, weights=weights, k=1)[0]


def sample_weighted_unique(items: list, weights: list[float], k: int, rng: random.Random | None = None) -> list:
    """Weighted sampling without replacement, no duplicates."""
    rng = rng or random
    _validate_weights(weights)
    pool = [(it, w) for it, w in zip(items, weights) if w > 0]
    if not pool:
        # fallback: uniform unique sample
        pool = [(it, 1.0) for it in items]
    k = min(k, len(pool))
    out = []
    pool = list(pool)
    for _ in range(k):
        its = [p[0] for p in pool]
        wts = [p[1] for p in pool]
        pick = choose_weighted(its, wts, rng)
        out.append(pick)
        pool = [p for p in pool if p[0] != pick]
    return out
