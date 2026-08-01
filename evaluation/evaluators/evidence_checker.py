#!/usr/bin/env python3
"""Evidence checker — validates that Claude output cites real evidence."""

from typing import Dict, List


def check_evidence(response: Dict) -> List[str]:
    errors: List[str] = []

    evidence = response.get("evidence_used", [])
    if not evidence:
        errors.append("MISSING: evidence_used is empty")
        return errors

    for i, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence_used[{i}] is not a dict")
            continue
        if "source" not in item:
            errors.append(f"evidence_used[{i}] missing 'source'")
        if "fact" not in item:
            errors.append(f"evidence_used[{i}] missing 'fact'")

    # Layer 2 must cite at least one evidence
    layer2 = response.get("layer2", {}).get("content", "")
    if layer2 and not any(item.get("fact", "") in layer2 for item in evidence if item.get("fact")):
        # Loose check: any evidence word overlap with layer2
        words_in_layer2 = set(layer2)
        overlap = any(
            any(w in words_in_layer2 for w in item.get("fact", ""))
            for item in evidence
        )
        if not overlap:
            errors.append("WARNING: layer2 does not reference any evidence_used fact")

    return errors
