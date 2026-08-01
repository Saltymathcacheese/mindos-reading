#!/usr/bin/env python3
"""
MindOS analysis_state.yaml updater.

Responsibilities:
- Load YAML safely via ruamel.yaml
- Validate required structure
- Backup previous state
- Update analysis state
- Atomic write
- Output JSON only

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

# ----------------------------
# Logging
# ----------------------------
logger = logging.getLogger("mindos.state_update")


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


class StateValidationError(Exception):
    """analysis_state.yaml structure invalid."""


# ----------------------------
# YAML State Manager
# ----------------------------
class YAMLStateManager:
    """Encapsulated YAML I/O — no module-level global state.
    Consistent with preflight.py's YAMLLoader pattern."""

    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

    def load(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"State file not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            data = self.yaml.load(f)
        if not isinstance(data, dict):
            raise StateValidationError("analysis_state.yaml root must be mapping")
        return data

    def save(self, path: Path, data: dict[str, Any]) -> None:
        directory = path.parent
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            delete=False,
        ) as tmp:
            self.yaml.dump(data, tmp)
            temp_name = tmp.name
        Path(temp_name).replace(path)


def validate_state(state: dict[str, Any]) -> None:
    """
    Minimal schema validation.
    Do not enforce full schema — MindOS state can evolve.
    """
    required_sections = [
        "last_analysis",
        "metrics",
        "data_sufficiency",
    ]
    missing = [s for s in required_sections if s not in state]
    if missing:
        raise StateValidationError(f"Missing sections: {missing}")


# ----------------------------
# Backup
# ----------------------------
def create_backup(state_path: Path) -> Path:
    backup_path = state_path.with_suffix(".yaml.backup")
    shutil.copy2(state_path, backup_path)
    logger.info("Backup created: %s", backup_path)
    return backup_path


# ----------------------------
# Update Logic
# ----------------------------
def update_state(
    state: dict[str, Any],
    *,
    total_hours: float | None = None,
    books_active: int | None = None,
    notes_total: int | None = None,
    diary_count: int | None = None,
    trend: str = "stable",
) -> dict[str, Any]:
    today = datetime.now().strftime("%Y-%m-%d")
    session_id = f"mindos-{today}"

    # last_analysis
    state["last_analysis"]["date"] = today
    state["last_analysis"]["session_id"] = session_id

    # metrics.reading
    reading = state.setdefault("metrics", {}).setdefault("reading", {})
    if total_hours is not None:
        reading["total_hours_30d"] = {
            "value": total_hours,
            "trend": trend,
            "confidence": 1.0,
        }
    if books_active is not None:
        reading["books_active"] = {
            "value": books_active,
            "trend": trend,
            "confidence": 1.0,
        }
    if notes_total is not None:
        reading["notes_total"] = {
            "value": notes_total,
            "trend": trend,
            "confidence": 1.0,
        }

    # data sufficiency
    if diary_count is not None:
        state.setdefault("data_sufficiency", {})["diary_entries_total"] = diary_count

    # session counter
    metrics = state.setdefault("metrics", {})
    metrics["session_count"] = metrics.get("session_count", 0) + 1

    return state


# ----------------------------
# Atomic Write
# ----------------------------
def atomic_write_yaml(path: Path, data: dict[str, Any]) -> None:
    manager = YAMLStateManager()
    manager.save(path, data)


# ----------------------------
# CLI
# ----------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Update MindOS analysis state")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--total-hours", type=float)
    parser.add_argument("--books-active", type=int)
    parser.add_argument("--notes-total", type=int)
    parser.add_argument("--diary-count", type=int)
    parser.add_argument("--trend", default="stable")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        vault = Path(args.vault_root)
        state_path = vault / "7-System" / "analysis_state.yaml"

        manager = YAMLStateManager()
        create_backup(state_path)
        state = manager.load(state_path)
        validate_state(state)

        updated = update_state(
            state,
            total_hours=args.total_hours,
            books_active=args.books_active,
            notes_total=args.notes_total,
            diary_count=args.diary_count,
            trend=args.trend,
        )

        manager.save(state_path, updated)

        print(
            json.dumps(
                {
                    "success": True,
                    "updated": str(state_path),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                },
                ensure_ascii=False,
            )
        )
    except Exception as e:
        logger.exception("State update failed")
        print(
            json.dumps(
                {"success": False, "error": str(e)},
                ensure_ascii=False,
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
