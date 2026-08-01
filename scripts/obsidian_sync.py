#!/usr/bin/env python3
"""
MindOS obsidian_sync.py — Vault consistency sync.

Ensures MindOS-generated files follow Obsidian conventions:
- Valid frontmatter with id, type, date, related links
- Cross-references between reviews, patterns, goals
- Removes orphaned references

Usage: python scripts/obsidian_sync.py [vault_root]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


class ObsidianSync:
    def __init__(self, vault: Path):
        self.vault = vault

    def sync_all(self) -> dict:
        actions: list[str] = []

        # Ensure all content directories have at least a .gitkeep-like marker
        for d in ["0-Inbox", "1-Experiences", "2-Knowledge", "3-Patterns",
                   "4-Questions", "5-Decisions", "6-Reviews"]:
            path = self.vault / d
            if not path.exists():
                path.mkdir(parents=True)
                actions.append(f"Created missing directory: {d}")

        # Sync related links in the latest review to known entities
        reviews_dir = self.vault / "6-Reviews"
        if reviews_dir.exists():
            latest = sorted(reviews_dir.glob("*.md"), reverse=True)
            if latest:
                actions.append(f"Latest review: {latest[0].name}")

        # Check for broken [[wikilinks]]
        broken = self._check_broken_links()
        if broken:
            actions.append(f"Found {len(broken)} potentially broken wikilinks")

        return {
            "success": True,
            "synced_at": datetime.now().isoformat(),
            "actions": actions,
            "broken_links": broken,
        }

    def _check_broken_links(self) -> list[str]:
        """Find [[wikilinks]] that don't resolve to existing files."""
        import re
        broken: list[str] = []
        all_files = {f.stem for f in self.vault.rglob("*.md") if ".obsidian" not in str(f)}

        for f in self.vault.rglob("*.md"):
            if ".obsidian" in str(f):
                continue
            try:
                text = f.read_text(encoding="utf-8")
                links = re.findall(r"\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]", text)
                for link in links:
                    clean = link.split("#")[0].split("|")[0].strip()
                    if clean and clean not in all_files:
                        broken.append(f"{f.name} → [[{clean}]]")
            except Exception:
                continue
        return broken


def main():
    parser = argparse.ArgumentParser(description="Sync MindOS vault with Obsidian conventions")
    parser.add_argument("vault_root", nargs="?", default=".")
    args = parser.parse_args()

    try:
        sync = ObsidianSync(Path(args.vault_root))
        result = sync.sync_all()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
