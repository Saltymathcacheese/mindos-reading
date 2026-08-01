#!/usr/bin/env python3
"""Confidence checker — low confidence must use uncertain language."""

from typing import Dict, List

CONFIDENCE_UNCERTAINTY = {
    "L0": ["推测", "可能", "不确定"],
    "L1": ["可能", "初步信号", "观察到", "尚需"],
}

CONFIDENCE_FORBIDDEN = {
    "L0": ["证明", "说明", "一定", "就是", "表明", "显示"],
    "L1": ["证明", "说明", "一定", "就是", "充分证明"],
}


def check_confidence(response: Dict) -> List[str]:
    errors: List[str] = []

    for layer in ("layer1", "layer2", "layer3"):
        item = response.get(layer, {})
        if not isinstance(item, dict):
            errors.append(f"{layer} is not a dict")
            continue

        confidence = item.get("confidence", "")
        content = item.get("content", "")

        if not confidence:
            errors.append(f"{layer} missing confidence")
            continue

        # Check that confidence level is valid
        if confidence not in ("L0", "L1", "L2", "L3", "L4"):
            errors.append(f"{layer} invalid confidence: {confidence}")
            continue

        # For low confidence, must use uncertainty words (loose check)
        if confidence in CONFIDENCE_UNCERTAINTY:
            uncertainty_words = CONFIDENCE_UNCERTAINTY[confidence]
            if not any(w in content for w in uncertainty_words):
                errors.append(
                    f"{layer} ({confidence}) should use uncertainty: {uncertainty_words}"
                )

        # For low confidence, must NOT use certainty words
        if confidence in CONFIDENCE_FORBIDDEN:
            forbidden_words = CONFIDENCE_FORBIDDEN[confidence]
            for word in forbidden_words:
                if word in content:
                    errors.append(f"{layer} ({confidence}) overclaim: '{word}' in '{content[:40]}...'")
                    break

    return errors
