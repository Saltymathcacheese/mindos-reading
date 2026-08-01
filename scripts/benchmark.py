#!/usr/bin/env python3
"""
MindOS benchmark.py — System-wide regression and quality benchmark.

Runs all tests + evaluation suites and produces a single quality score.
Used before any version upgrade to detect regressions.

Usage: python scripts/benchmark.py [vault_root]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_pytest(vault: Path) -> dict:
    """Run pytest and parse results."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
        capture_output=True, text=True, cwd=str(vault),
    )
    # Parse: "102 passed in 1.5s"
    output = result.stdout.strip() + result.stderr.strip()
    passed = 0
    failed = 0
    for line in output.split("\n"):
        if "passed" in line:
            try:
                passed = int(line.split("passed")[0].strip().split()[-1])
            except (ValueError, IndexError):
                pass
        if "failed" in line:
            try:
                failed = int(line.split("failed")[0].strip().split()[-1])
            except (ValueError, IndexError):
                pass

    return {
        "passed": passed,
        "failed": failed,
        "total": passed + failed,
        "exit_code": result.returncode,
    }


def run_evaluator(vault: Path) -> dict:
    """Run cognitive evaluator."""
    result = subprocess.run(
        [sys.executable, "scripts/evaluator.py", str(vault), "--suite", "safety"],
        capture_output=True, text=True, cwd=str(vault),
    )
    try:
        # evaluator outputs full JSON object — it may be multi-line
        output = result.stdout.strip()
        # Try parsing the entire stdout as JSON
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            # Fall back: find line starting with { and containing "success"
            for line in output.split("\n"):
                stripped = line.strip()
                if stripped.startswith("{") and '"success"' in stripped:
                    data = json.loads(stripped)
                    break
            else:
                return {"total": 0, "passed": 0, "failed": 0, "error": "json not found in output"}

        safety = data.get("results", {})
        return {
            "total": safety.get("total", 0),
            "passed": safety.get("passed", 0),
            "failed": safety.get("failed", 0),
        }
    except (json.JSONDecodeError, IndexError) as e:
        return {"total": 0, "passed": 0, "failed": 0, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Run MindOS benchmark suite")
    parser.add_argument("vault_root", nargs="?", default=".")
    args = parser.parse_args()

    vault = Path(args.vault_root)

    pytest_result = run_pytest(vault)
    eval_result = run_evaluator(vault)

    overall_passed = pytest_result["passed"] + eval_result["passed"]
    overall_total = pytest_result["total"] + eval_result["total"]
    score = round(overall_passed / overall_total * 100, 1) if overall_total > 0 else 0

    report = {
        "version": "3.4",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "pytest": pytest_result,
        "evaluator": eval_result,
        "overall": {
            "passed": overall_passed,
            "total": overall_total,
            "score": score,
            "grade": "A" if score >= 95 else "B" if score >= 80 else "C" if score >= 60 else "F",
        },
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
