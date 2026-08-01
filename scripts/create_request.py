#!/usr/bin/env python3
"""
MindOS create_request.py — Generate analysis_request.json from Evidence Bundle.

Reads 7-System/analysis_context.json and produces handoff/analysis_request.json
for Claude to consume with references/.

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def create_request(context_path: Path, output_path: Path) -> dict:
    """Build analysis_request.json from evidence bundle."""
    if not context_path.exists():
        raise FileNotFoundError(f"Context not found: {context_path} — run analysis_context.py first")

    bundle = json.loads(context_path.read_text(encoding="utf-8"))
    runtime = bundle.get("runtime", {})
    mode = runtime.get("mode", "V0.1")

    # Task requirements by version
    requirements = ["surface_analysis", "association_analysis", "narrative_analysis", "reflection_question"]
    pattern_allowed = mode in ("V0.2", "V0.3")

    request = {
        "protocol_version": "1.0",
        "created_at": datetime.now().isoformat(),
        "mode": mode,
        "task": {
            "type": "reading_analysis",
            "requirements": requirements,
        },
        "evidence": bundle.get("evidence", {}),
        "constraints": {
            "no_diagnosis": True,
            "no_personality_label": True,
            "pattern_creation": pattern_allowed,
            "max_reflection_chars": 60,
        },
    }

    output_path.write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
    return request


def main():
    parser = argparse.ArgumentParser(description="Generate MindOS analysis request for Claude")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--output", default=None, help="Output path (default: handoff/analysis_request.json)")
    args = parser.parse_args()

    vault = Path(args.vault_root)
    context_path = vault / "7-System" / "analysis_context.json"
    output_path = Path(args.output) if args.output else (vault / "handoff" / "analysis_request.json")

    try:
        request = create_request(context_path, output_path)
        print(json.dumps({"success": True, "path": str(output_path), "mode": request["mode"]}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
