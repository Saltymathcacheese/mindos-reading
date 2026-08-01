#!/usr/bin/env python3
"""
MindOS prediction_tracker.py — Track hypothesis predictions for later validation.

Creates new prediction records in prediction_history.yaml.
Checks existing predictions against new evidence.

Usage: python scripts/prediction_tracker.py [vault_root] [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from ruamel.yaml import YAML
except ImportError:
    YAML = None


class PredictionTracker:
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

    def create(self, hypothesis: str, evidence: list[str], confidence: str = "L1") -> dict:
        preds = self._load_yaml(self.vault / "7-System" / "prediction_history.yaml")
        predictions = preds.get("predictions", [])

        pred_id = f"pred-{datetime.now().strftime('%Y%m%d')}-{len(predictions)+1:03d}"

        new_pred = {
            "id": pred_id,
            "hypothesis": hypothesis,
            "evidence": evidence,
            "confidence": confidence,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "validation_window_days": 30,
            "check_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": "monitoring",
            "resolution": None,
            "user_feedback": None,
            "user_correction": None,
            "calibration_impact": None,
        }
        predictions.append(new_pred)
        preds["predictions"] = predictions
        self._save_yaml(self.vault / "7-System" / "prediction_history.yaml", preds)

        return new_pred

    def check_expired(self) -> list[dict]:
        """Find monitoring predictions past their check_date and mark as expired."""
        preds = self._load_yaml(self.vault / "7-System" / "prediction_history.yaml")
        predictions = preds.get("predictions", [])
        updated = []

        for p in predictions:
            if p.get("status") == "monitoring" and p.get("check_date"):
                try:
                    check = datetime.strptime(p["check_date"], "%Y-%m-%d")
                    if datetime.now() >= check:
                        p["status"] = "expired"
                        p["resolution"] = "No confirming or disconfirming evidence within validation window"
                        updated.append(p)
                except ValueError:
                    continue

        if updated:
            self._save_yaml(self.vault / "7-System" / "prediction_history.yaml", preds)

        return updated


def main():
    parser = argparse.ArgumentParser(description="Track MindOS predictions")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--check", action="store_true", help="Check for expired predictions")
    parser.add_argument("--create", action="store_true", help="Create a new prediction")
    parser.add_argument("--hypothesis", default="", help="Hypothesis text")
    parser.add_argument("--evidence", default="[]", help="JSON array of evidence strings")
    parser.add_argument("--confidence", default="L1")
    args = parser.parse_args()

    vault = Path(args.vault_root)
    tracker = PredictionTracker(vault)

    try:
        if args.check:
            expired = tracker.check_expired()
            print(json.dumps({"success": True, "expired": len(expired)}, ensure_ascii=False))
        elif args.create:
            evidence = json.loads(args.evidence)
            pred = tracker.create(args.hypothesis, evidence, args.confidence)
            print(json.dumps({"success": True, "prediction": pred}, ensure_ascii=False, indent=2))
        else:
            preds = tracker._load_yaml(vault / "7-System" / "prediction_history.yaml")
            total = len(preds.get("predictions", []))
            monitoring = len([p for p in preds.get("predictions", []) if p.get("status") == "monitoring"])
            print(json.dumps({"success": True, "total": total, "monitoring": monitoring}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
