#!/usr/bin/env python3
"""
MindOS init.py — First-run vault initializer.

Creates all required directories and seeds analysis_state.yaml.
Safe to run on an existing vault (directories use exist_ok=True).

Usage: python scripts/init.py [--vault .]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DIRECTORIES = [
    "0-Inbox",
    "1-Experiences",
    "2-Knowledge",
    "3-Patterns",
    "4-Questions",
    "5-Decisions",
    "6-Reviews",
    "7-System",
    "7-System/raw_evidence",
    "8-Goals",
    "9-Actions",
    "10-Memory",
    "11-Capture/images",
    "11-Capture/audio",
    "11-Capture/pdf",
    "12-Knowledge-Map",
    "handoff",
    "schemas",
    "evaluation/evaluators",
    "evaluation/golden_cases",
    "evaluation/expected_outputs",
]

STATE_TEMPLATE = """\
version: "4.1"
last_analysis:
  date: null
  session_id: null
  mode: "V0.1"

data_sufficiency:
  diary_entries_total: 0
  patterns_confirmed: 0
  actions_attempted: 0

metrics:
  reading:
    total_hours_30d: {value: 0, trend: unknown, confidence: 1.0}
    books_active: {value: 0, trend: unknown, confidence: 1.0}
    fiction_ratio: {value: 0, trend: unknown, confidence: 0.9}
    notes_total: {value: 0, trend: unknown, confidence: 1.0}
  diary:
    entry_count_30d: {value: 0, trend: unknown, confidence: 1.0}
    avg_words_per_entry: {value: 0, trend: unknown, confidence: 0.85}
  learning:
    study_hours_weekly: {value: null, trend: unknown, confidence: 0.0}
    flashcard_completion_rate: {value: null, trend: unknown, confidence: 0.0}
  session_count: 0

emotion_signals:
  anxiety: {frequency: unknown, trend: unknown, confidence: 0.0}
  fatigue: {frequency: unknown, trend: unknown, confidence: 0.0}
  motivation: {frequency: unknown, trend: unknown, confidence: 0.0}
  curiosity: {frequency: unknown, trend: unknown, confidence: 0.0}

active_themes: []
pending_hypotheses: []

system_self_check:
  pattern_accuracy_3month: null
  user_overrides_3month: 0
  feedback_rate_3month: null
  mode: "normal"
  last_mode_change: null
  mode_change_reason: null
"""


def initialize(root: Path) -> dict:
    created: list[str] = []
    skipped: list[str] = []

    for folder in DIRECTORIES:
        p = root / folder
        if p.exists():
            skipped.append(folder)
        else:
            p.mkdir(parents=True)
            created.append(folder)

    state_path = root / "7-System" / "analysis_state.yaml"
    if not state_path.exists():
        state_path.write_text(STATE_TEMPLATE, encoding="utf-8")
        created.append("7-System/analysis_state.yaml (seed)")
    else:
        skipped.append("7-System/analysis_state.yaml (exists)")

    return {"created": created, "skipped": skipped}


def main():
    parser = argparse.ArgumentParser(description="Initialize MindOS vault")
    parser.add_argument("--vault", default=".", help="Vault root path")
    args = parser.parse_args()

    try:
        vault = Path(args.vault)
        result = initialize(vault)
        print(
            json.dumps(
                {
                    "success": True,
                    "created": len(result["created"]),
                    "skipped": len(result["skipped"]),
                    "created_dirs": result["created"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
