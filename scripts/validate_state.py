#!/usr/bin/env python3
"""
MindOS validate_state.py — Dual-layer state validation.

Validates analysis_state.yaml against:
1. JSON Schema (structural contract)
2. Business rules (semantic constraints)

Usage: python scripts/validate_state.py <vault_root>
Output: {"success": true, "schema_errors": [], "rule_errors": []}

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

try:
    from jsonschema import validate, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# =========================
# Logging
# =========================
logger = logging.getLogger("mindos.validate_state")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# =========================
# Validator
# =========================
class StateValidator:
    def __init__(self, schema_path: Path | None = None):
        self.schema: dict | None = None
        if schema_path and schema_path.exists():
            self.schema = json.loads(schema_path.read_text(encoding="utf-8"))

    # ── Schema Validation ──

    def validate_schema(self, data: dict[str, Any]) -> list[str]:
        """JSON Schema validation. Returns list of error messages (empty = valid)."""
        if not self.schema or not HAS_JSONSCHEMA:
            return []  # schema validation skipped — jsonschema not installed or schema missing
        try:
            validate(data, self.schema)
            return []
        except ValidationError as e:
            return [str(e)]

    # ── Business Rule Validation ──

    def validate_rules(self, data: dict[str, Any]) -> list[str]:
        """Semantic rule checks. Returns list of violation messages."""
        errors: list[str] = []

        # Rule 1: diary count cannot be negative
        ds = data.get("data_sufficiency", {})
        diary = ds.get("diary_entries_total", 0)
        if isinstance(diary, (int, float)) and diary < 0:
            errors.append("diary_entries_total cannot be negative")

        # Rule 2: patterns_confirmed cannot be negative
        pc = ds.get("patterns_confirmed", 0)
        if isinstance(pc, (int, float)) and pc < 0:
            errors.append("patterns_confirmed cannot be negative")

        # Rule 3: last_analysis.date should be present if session_count > 0
        last = data.get("last_analysis", {})
        session_count = data.get("metrics", {}).get("session_count", 0)
        if session_count and session_count > 0 and not last.get("date"):
            errors.append("session_count > 0 but last_analysis.date is missing")

        # Rule 4: last_analysis.mode must be valid if present
        mode = last.get("mode")
        if mode and mode not in ("V0.1", "V0.2", "V0.3"):
            errors.append(f"Invalid mode: {mode} (expected V0.1|V0.2|V0.3)")

        # Rule 5: system_self_check.mode must be valid if present
        ssc = data.get("system_self_check", {})
        ssc_mode = ssc.get("mode")
        if ssc_mode and ssc_mode not in ("normal", "cautious", "safe"):
            errors.append(f"Invalid system_self_check.mode: {ssc_mode}")

        return errors

    # ── Full Validation ──

    def validate(self, data: dict[str, Any]) -> dict:
        schema_errors = self.validate_schema(data)
        rule_errors = self.validate_rules(data)
        all_ok = len(schema_errors) == 0 and len(rule_errors) == 0
        return {
            "success": all_ok,
            "schema_errors": schema_errors,
            "rule_errors": rule_errors,
        }


# =========================
# CLI
# =========================
def main():
    parser = argparse.ArgumentParser(description="Validate MindOS analysis state")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    vault = Path(args.vault_root)
    state_path = vault / "7-System" / "analysis_state.yaml"
    schema_path = vault / "schemas" / "analysis_state.schema.json"

    try:
        if not state_path.exists():
            print(json.dumps({"success": False, "error": "analysis_state.yaml not found"}))
            sys.exit(1)

        yaml = YAML()
        with state_path.open("r", encoding="utf-8") as f:
            data = yaml.load(f)

        validator = StateValidator(schema_path)
        result = validator.validate(data)
        print(json.dumps(result, ensure_ascii=False))
        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        logger.exception("Validation failed")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
