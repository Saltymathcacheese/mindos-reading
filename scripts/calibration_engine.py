#!/usr/bin/env python3
"""
MindOS calibration_engine.py — Self-calibration calculator.

Computes MindOS accuracy from prediction + feedback history,
adjusts confidence multiplier, and detects bias patterns.

Usage: python scripts/calibration_engine.py [vault_root]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from ruamel.yaml import YAML
except ImportError:
    YAML = None


class CalibrationEngine:
    def __init__(self, vault: Path):
        self.vault = vault

    def _load_yaml(self, path: Path) -> dict:
        if not path.exists():
            return {}
        if YAML:
            yaml = YAML()
            with path.open("r", encoding="utf-8") as f:
                return yaml.load(f) or {}
        return {}

    def _save_yaml(self, path: Path, data: dict) -> None:
        if YAML:
            yaml = YAML()
            with path.open("w", encoding="utf-8") as f:
                yaml.dump(data, f)

    def compute(self) -> dict:
        # Load data
        cal = self._load_yaml(self.vault / "7-System" / "calibration.yaml")
        preds = self._load_yaml(self.vault / "7-System" / "prediction_history.yaml")
        feedback = self._load_yaml(self.vault / "7-System" / "feedback_history.yaml")

        predictions = preds.get("predictions", [])
        fb_entries = feedback.get("feedback", [])

        # Count resolved predictions
        resolved = [p for p in predictions if p.get("status") not in ("monitoring", None)]
        confirmed = [p for p in resolved if p.get("status") == "confirmed"]
        rejected = [p for p in resolved if p.get("status") == "rejected"]
        partial = [p for p in resolved if p.get("status") == "partially_correct"]

        total = len(resolved)
        accuracy = round(len(confirmed) / total, 2) if total > 0 else None

        # Count user corrections
        corrections = [f for f in fb_entries if f.get("user_response") in ("corrected", "rejected")]

        # Adjust confidence multiplier
        mult = 1.0
        if accuracy is not None:
            if accuracy < 0.3:
                mult = 0.5
            elif accuracy < 0.5:
                mult = 0.7
            elif accuracy < 0.7:
                mult = 0.85

        # Bias detection: which identities get rejected most?
        identity_rejections: dict[str, int] = {}
        for f in fb_entries:
            target = f.get("target", {})
            if isinstance(target, dict):
                ident = target.get("identity", "unknown")
                if f.get("user_response") in ("corrected", "rejected"):
                    identity_rejections[ident] = identity_rejections.get(ident, 0) + 1

        over_estimated = [k for k, v in identity_rejections.items() if v >= 2]

        # Update calibration state
        cal["calibration"]["overall"] = {
            "total_predictions": total,
            "confirmed": len(confirmed),
            "partially_correct": len(partial),
            "rejected": len(rejected),
            "accuracy": accuracy,
            "last_updated": datetime.now().isoformat(),
        }
        cal["calibration"]["confidence_multiplier"] = mult
        cal["calibration"]["bias_profile"]["over_estimates"] = over_estimated
        cal["calibration"]["bias_profile"]["last_bias_check"] = datetime.now().isoformat()

        # Safe mode check
        should_safe = (
            (accuracy is not None and accuracy < 0.5)
            or len(corrections) > 5
        )
        cal["calibration"]["safe_mode"]["active"] = should_safe

        self._save_yaml(self.vault / "7-System" / "calibration.yaml", cal)

        return {
            "total_predictions": total,
            "accuracy": accuracy,
            "confidence_multiplier": mult,
            "corrections": len(corrections),
            "over_estimated_identities": over_estimated,
            "safe_mode": should_safe,
        }


def main():
    parser = argparse.ArgumentParser(description="Run MindOS calibration engine")
    parser.add_argument("vault_root", nargs="?", default=".")
    args = parser.parse_args()

    try:
        engine = CalibrationEngine(Path(args.vault_root))
        result = engine.compute()
        print(json.dumps({"success": True, **result}, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
