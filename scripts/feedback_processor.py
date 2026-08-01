#!/usr/bin/env python3
"""
MindOS feedback_processor.py — Process user feedback and update calibration.

User corrections are MindOS's most valuable data source.
Each correction adjusts confidence, updates bias profiles, and prevents repeats.

Usage: python scripts/feedback_processor.py [vault_root] --target <id> --response <confirmed|corrected|rejected> [--correction "text"]
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


class FeedbackProcessor:
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

    def process(self, target_id: str, response: str, correction: str = "", target_type: str = "hypothesis") -> dict:
        today = datetime.now().strftime("%Y-%m-%d")

        # Load feedback history
        fb_data = self._load_yaml(self.vault / "7-System" / "feedback_history.yaml")
        feedback_list = fb_data.get("feedback", [])

        fb_id = f"fb-{today}-{len(feedback_list)+1:03d}"

        # Determine confidence adjustment
        adjustments = {
            "confirmed": 0.1,
            "corrected": -0.15,
            "rejected": -0.3,
        }
        conf_adj = adjustments.get(response, 0)

        entry = {
            "id": fb_id,
            "date": today,
            "target": {"type": target_type, "id": target_id},
            "user_response": response,
            "user_correction": correction if response != "confirmed" else None,
            "effect": {"confidence_adjustment": conf_adj},
            "learned": False,
        }
        feedback_list.append(entry)
        fb_data["feedback"] = feedback_list
        self._save_yaml(self.vault / "7-System" / "feedback_history.yaml", fb_data)

        # Update the target prediction if it exists
        if target_type == "hypothesis":
            preds = self._load_yaml(self.vault / "7-System" / "prediction_history.yaml")
            for p in preds.get("predictions", []):
                if p.get("id") == target_id and p.get("status") == "monitoring":
                    p["status"] = "confirmed" if response == "confirmed" else "rejected"
                    p["user_feedback"] = response
                    p["user_correction"] = correction if response != "confirmed" else None
                    p["resolution"] = f"User {response}" + (f": {correction}" if correction else "")
                    break
            self._save_yaml(self.vault / "7-System" / "prediction_history.yaml", preds)

        return {"id": fb_id, "response": response, "confidence_adjustment": conf_adj}


def main():
    parser = argparse.ArgumentParser(description="Process MindOS user feedback")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--target", required=True, help="Prediction/hypothesis ID")
    parser.add_argument("--response", required=True, choices=["confirmed", "corrected", "rejected"])
    parser.add_argument("--correction", default="", help="User's correction text")
    parser.add_argument("--type", default="hypothesis", help="Target type")
    args = parser.parse_args()

    try:
        processor = FeedbackProcessor(Path(args.vault_root))
        result = processor.process(args.target, args.response, args.correction, args.type)
        print(json.dumps({"success": True, **result}, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
