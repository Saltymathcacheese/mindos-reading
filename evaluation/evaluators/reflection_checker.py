#!/usr/bin/env python3
"""Reflection checker — one open-ended question, ≤50 characters (Chinese)."""

from typing import List


def check_reflection(question: str) -> List[str]:
    errors: List[str] = []

    if not question or not question.strip():
        errors.append("reflection is empty")
        return errors

    # Length
    if len(question) > 50:
        errors.append(f"reflection too long: {len(question)} chars (max 50)")

    # Must be a question
    question_marks = question.count("?") + question.count("？")
    if question_marks == 0:
        has_question_word = any(w in question for w in ["吗", "什么", "如何", "怎么", "是否"])
        if not has_question_word:
            errors.append("reflection must be a question")

    # Must not be closed (yes/no only — too narrow)
    if question.strip().endswith("吗？") and len(question.strip()) <= 8:
        errors.append("reflection too closed — ask an open question")

    return errors
