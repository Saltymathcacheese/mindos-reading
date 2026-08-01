#!/usr/bin/env python3
"""Memory validator — ensures memory entries respect MindOS safety boundaries.

Checks:
- No diagnostic language
- No personality labels
- Has source references
- Score is in valid range
"""

from typing import Dict, List

FORBIDDEN_MEMORY: List[str] = [
    "你是", "你有", "你的人格", "你正在逃避", "你就是",
    "完美主义", "逃避型", "焦虑型", "回避型",
]


def validate_memory(entry: Dict) -> List[str]:
    errors = []

    content = entry.get("content", "")

    # Safety
    for phrase in FORBIDDEN_MEMORY:
        if phrase in content:
            errors.append(f"Forbidden in memory: '{phrase}'")

    # Source
    source = entry.get("source", [])
    if not source:
        errors.append("Memory must have at least one source")

    # Score
    score = entry.get("score", 0)
    if not (0 <= score <= 10):
        errors.append(f"Invalid score: {score} (must be 0-10)")

    # Status
    status = entry.get("status")
    if status not in ("candidate", "active", "dormant", "archived"):
        errors.append(f"Invalid status: {status}")

    return errors


def validate_batch(entries: List[Dict]) -> Dict[str, List[str]]:
    results = {}
    for i, entry in enumerate(entries):
        eid = entry.get("id", f"entry_{i}")
        errs = validate_memory(entry)
        if errs:
            results[eid] = errs
    return results
