#!/usr/bin/env python3
"""
MindOS validate_report.py — Claude output contract validator.

Validates Claude-generated report JSON against report.schema.json
before it gets rendered to Markdown and saved to the vault.

Usage: python scripts/validate_report.py --input report.json [--schema schemas/report.schema.json]
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


class ReportValidator:
    def __init__(self, schema_path: Path):
        self.schema = json.loads(schema_path.read_text(encoding="utf-8"))

    def validate(self, data: dict) -> list[str]:
        errors: list[str] = []

        if not HAS_JSONSCHEMA:
            return errors  # jsonschema not installed — skip structural validation

        try:
            validate(data, self.schema)
        except ValidationError as e:
            errors.append(str(e))

        # Extra rules beyond JSON Schema
        reflection = data.get("reflection", "")
        if reflection:
            # Reflection should be a question (contain "?" or "吗" or "什么" or "如何")
            if not any(c in reflection for c in ["?", "？", "吗", "什么", "如何", "怎么", "是否"]):
                errors.append("reflection should be a question")

            # Should not contain diagnostic language
            forbidden = ["你是", "你有", "你的问题是", "你缺乏", "你就是", "你这个人"]
            for word in forbidden:
                if word in reflection:
                    errors.append(f"reflection contains forbidden diagnostic phrase: '{word}'")

        return errors


def main():
    parser = argparse.ArgumentParser(description="Validate MindOS report JSON")
    parser.add_argument("--input", required=True, help="Report JSON file path")
    parser.add_argument("--schema", default="schemas/report.schema.json", help="Schema file path")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        validator = ReportValidator(Path(args.schema))
        errors = validator.validate(data)

        print(
            json.dumps(
                {"success": len(errors) == 0, "errors": errors},
                ensure_ascii=False,
                indent=2,
            )
        )
        if errors:
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"success": False, "errors": [str(e)]}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
