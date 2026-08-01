#!/usr/bin/env python3
"""
MindOS preflight.py — Runtime context loader.

Responsibilities:
- Load analysis_state.yaml via ruamel.yaml
- Detect MindOS version mode (V0.1/V0.2/V0.3)
- Extract runtime information
- Provide safe fallback on error

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

# =========================
# Logging
# =========================
logger = logging.getLogger("mindos.preflight")


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# =========================
# Runtime Context
# =========================
@dataclass
class RuntimeContext:
    mode: str                # V0.1 | V0.2 | V0.3
    diary_count: int
    patterns_confirmed: int
    last_analysis: str | None
    safe_mode: bool = False
    error: str | None = None


# =========================
# YAML Loader
# =========================
class YAMLLoader:
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

    def load(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(str(path))
        with path.open("r", encoding="utf-8") as f:
            data = self.yaml.load(f)
        if not isinstance(data, dict):
            raise ValueError("Invalid YAML root")
        return data


# =========================
# State Extractor
# =========================
class StateReader:
    @staticmethod
    def _get_value(data: dict, path: list[str], default=None):
        """Safe nested dict access."""
        current = data
        for key in path:
            if not isinstance(current, dict):
                return default
            current = current.get(key)
            if current is None:
                return default
        return current

    def extract_context(self, state: dict[str, Any]) -> RuntimeContext:
        # ── Data sufficiency ──
        diary_count = int(
            self._get_value(
                state, ["data_sufficiency", "diary_entries_total"], 0
            )
            or 0
        )
        patterns_confirmed = int(
            self._get_value(
                state, ["data_sufficiency", "patterns_confirmed"], 0
            )
            or 0
        )

        # ── Last analysis ──
        last_analysis = self._get_value(state, ["last_analysis", "date"])

        # ── Explicit mode override (if set in state) ──
        explicit_mode = self._get_value(state, ["last_analysis", "mode"])
        if explicit_mode and explicit_mode in ("V0.1", "V0.2", "V0.3"):
            mode = explicit_mode
        else:
            mode = self._detect_mode(diary_count, patterns_confirmed)

        # ── Safe mode check (system_self_check, separate from version) ──
        sys_mode = self._get_value(state, ["system_self_check", "mode"])
        safe_mode = sys_mode == "safe"

        return RuntimeContext(
            mode=mode,
            diary_count=diary_count,
            patterns_confirmed=patterns_confirmed,
            last_analysis=last_analysis,
            safe_mode=safe_mode,
        )

    @staticmethod
    def _detect_mode(diary_count: int, patterns_confirmed: int) -> str:
        """
        Version gating logic (must match SKILL.md dispatch table):

        V0.1: diary_entries_total < 10
        V0.2: diary_entries_total >= 10 AND patterns_confirmed < 3
        V0.3: patterns_confirmed >= 3
        """
        if patterns_confirmed >= 3:
            return "V0.3"
        if diary_count >= 10:
            return "V0.2"
        return "V0.1"


# =========================
# Safe Fallback
# =========================
def safe_context(error: Exception) -> RuntimeContext:
    return RuntimeContext(
        mode="V0.1",               # safest default: surface analysis only
        diary_count=0,
        patterns_confirmed=0,
        last_analysis=None,
        safe_mode=True,
        error=str(error),
    )


# =========================
# CLI
# =========================
def main():
    parser = argparse.ArgumentParser(
        description="MindOS preflight runtime loader"
    )
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    state_path = Path(args.vault_root) / "7-System" / "analysis_state.yaml"

    try:
        loader = YAMLLoader()
        state = loader.load(state_path)
        context = StateReader().extract_context(state)

        result = {
            "success": True,
            "mode": context.mode,
            "diary_count": context.diary_count,
            "patterns_confirmed": context.patterns_confirmed,
            "last_analysis": context.last_analysis,
            "safe_mode": context.safe_mode,
        }
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        logger.exception("Preflight failed")
        context = safe_context(e)
        print(
            json.dumps(
                {
                    "success": False,
                    "mode": context.mode,
                    "error": context.error,
                    "safe_mode": True,
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
