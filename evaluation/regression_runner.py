#!/usr/bin/env python3
"""
MindOS regression_runner.py — Unified evaluation pipeline.

Runs all four evaluators against a Claude analysis_response.json.
Used by: mindos.py evaluate, and integrated into analyze pipeline.

Usage: python evaluation/regression_runner.py [--input handoff/analysis_response.json]
Output: {"success": true/false, "checks": {...}, "total_errors": N}

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add parent to sys.path so evaluators can import
sys.path.insert(0, str(Path(__file__).resolve().parent))

from evaluators.evidence_checker import check_evidence
from evaluators.safety_checker import check_safety_structured
from evaluators.confidence_checker import check_confidence
from evaluators.reflection_checker import check_reflection


def evaluate(data: dict) -> dict:
    """Run all four evaluators. Returns {checks, total_errors}."""
    checks: dict[str, list[str]] = {}

    checks["evidence"] = check_evidence(data)
    checks["safety"] = check_safety_structured(data)
    checks["confidence"] = check_confidence(data)
    checks["reflection"] = check_reflection(data.get("reflection", ""))

    total = sum(len(v) for v in checks.values())

    return {
        "success": total == 0,
        "checks": checks,
        "total_errors": total,
    }


def main():
    parser = argparse.ArgumentParser(description="Run MindOS evaluation suite")
    parser.add_argument("--input", default="handoff/analysis_response.json", help="Response JSON to evaluate")
    parser.add_argument("--output", default=None, help="Write evaluation report to file")
    args = parser.parse_args()

    input_path = Path(args.input)

    try:
        if not input_path.exists():
            print(json.dumps({"success": False, "error": f"Response not found: {args.input}"}))
            sys.exit(1)

        data = json.loads(input_path.read_text(encoding="utf-8"))
        result = evaluate(data)

        output = json.dumps(result, ensure_ascii=False, indent=2)
        print(output)

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
