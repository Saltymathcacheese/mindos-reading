#!/usr/bin/env python3
"""Safety checker — blocks diagnostic language and personality labels."""

from typing import List

FORBIDDEN_PHRASES: List[str] = [
    "你就是",
    "你有心理问题",
    "你的人格是",
    "你正在逃避",
    "你是一个",
    "你缺乏",
]

FORBIDDEN_LABELS: List[str] = [
    "完美主义",
    "逃避型",
    "焦虑型",
    "回避型",
    "强迫症",
    "抑郁症",
    "人格障碍",
]


def check_safety(text: str) -> List[str]:
    """Check raw text for forbidden phrases and labels. Returns list of violations."""
    errors: List[str] = []

    for phrase in FORBIDDEN_PHRASES:
        if phrase in text:
            errors.append(f"FORBIDDEN PHRASE: '{phrase}'")

    for label in FORBIDDEN_LABELS:
        if label in text:
            errors.append(f"PERSONALITY LABEL: '{label}'")

    return errors


def check_safety_structured(response: dict) -> List[str]:
    """Check all text fields in a structured response."""
    errors: List[str] = []
    for field in ("layer1", "layer2", "layer3"):
        content = response.get(field, {}).get("content", "")
        errors += check_safety(content)
    errors += check_safety(response.get("reflection", ""))
    return errors
