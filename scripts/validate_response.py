#!/usr/bin/env python3
"""
MindOS validate_response.py — Claude output contract validator.

Validates Claude's analysis_response.json against claude_response.schema.json.
Performs dual validation: JSON Schema + semantic anti-diagnosis rules.

Usage: python scripts/validate_response.py --input analysis_response.json
Output: {"success": true/false, "errors": [...]}

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class ResponseValidator:
    def __init__(self, schema_path: Path):
        self.schema = json.loads(schema_path.read_text(encoding="utf-8"))

    def validate(self, data: dict) -> list[str]:
        errors: list[str] = []

        # ── JSON Schema ──
        if HAS_JSONSCHEMA:
            try:
                validate(data, self.schema)
            except ValidationError as e:
                errors.append(str(e))

        # ── Semantic rules ──
        DIAGNOSTIC = ["你是", "你有", "你的问题是", "你缺乏", "你就是", "你这个人", "你这种人"]
        PERSONALITY = ["完美主义", "逃避型", "焦虑型", "回避型", "强迫症", "抑郁症"]

        for field in ("layer1", "layer2", "layer3"):
            content = data.get(field, {}).get("content", "")
            for word in DIAGNOSTIC:
                if word in content:
                    errors.append(f"{field}.content contains forbidden diagnostic: '{word}'")
            for word in PERSONALITY:
                if word in content:
                    errors.append(f"{field}.content contains personality label: '{word}'")

        reflection = data.get("reflection", "")
        for word in DIAGNOSTIC:
            if word in reflection:
                errors.append(f"reflection contains forbidden diagnostic: '{word}'")

        # Reflection must be a question
        if reflection and not any(c in reflection for c in ["?", "？", "吗", "什么", "如何", "怎么", "是否"]):
            errors.append("reflection should be a question")

        # evidence_used must have at least one entry
        evidence = data.get("evidence_used", [])
        if len(evidence) == 0:
            errors.append("evidence_used must contain at least one source")

        return errors


def main():
    parser = argparse.ArgumentParser(description="Validate Claude analysis response")
    parser.add_argument("--input", required=True, help="analysis_response.json path")
    parser.add_argument("--schema", default="schemas/claude_response.schema.json", help="Schema path")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        validator = ResponseValidator(Path(args.schema))
        errors = validator.validate(data)

        print(json.dumps({"success": len(errors) == 0, "errors": errors}, ensure_ascii=False, indent=2))
        if errors:
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"success": False, "errors": [str(e)]}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
