#!/usr/bin/env python3
"""Memory score calculator — weighted multi-dimensional value assessment.

Formula: score = impact×0.30 + repetition×0.25 + future_relevance×0.35 + emotion×0.10
Future relevance weighted highest. Emotional weight kept low to avoid bias toward negatives.
"""

from typing import Dict


def calculate_score(item: Dict) -> float:
    impact = item.get("impact", 5)
    repetition = item.get("repetition", 1)
    future = item.get("future_relevance", 5)
    emotion = item.get("emotional_weight", 5)

    score = (
        impact * 0.30
        + repetition * 0.25
        + future * 0.35
        + emotion * 0.10
    )
    return round(score, 2)


def score_batch(candidates: list[Dict]) -> list[Dict]:
    """Score a batch of memory candidates, return sorted by score descending."""
    scored = []
    for c in candidates:
        s = calculate_score(c)
        scored.append({**c, "score": s})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def filter_top(scored: list[Dict], top_n: int = 5) -> list[Dict]:
    """Keep only top N scored memories."""
    return scored[:top_n]
