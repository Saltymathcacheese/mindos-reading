#!/usr/bin/env python3
"""
MindOS link_builder.py — Automatic wikilink injection.

Scans generated Markdown files and replaces known entity names
with Obsidian [[wikilinks]] based on existing vault content.

Usage: python scripts/link_builder.py [vault_root]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class LinkBuilder:
    def __init__(self, vault: Path):
        self.vault = vault
        self.link_index: dict[str, str] = self._build_index()

    def _build_index(self) -> dict[str, str]:
        """Scan vault for linkable entities: books, patterns, goals, questions."""
        index: dict[str, str] = {}

        # Scan 2-Knowledge/ for book notes
        knowledge_dir = self.vault / "2-Knowledge"
        if knowledge_dir.exists():
            for f in knowledge_dir.rglob("*.md"):
                name = f.stem
                index[name] = f"[[{name}]]"

        # Scan 3-Patterns/ (excluding INDEX)
        patterns_dir = self.vault / "3-Patterns"
        if patterns_dir.exists():
            for f in patterns_dir.glob("*.md"):
                if "INDEX" in f.name or "TEMPLATE" in f.name:
                    continue
                name = f.stem
                index[name] = f"[[{name}]]"

        # Scan 8-Goals/
        goals_dir = self.vault / "8-Goals"
        if goals_dir.exists():
            for f in goals_dir.glob("*.md"):
                if "INDEX" in f.name or "TEMPLATE" in f.name:
                    continue
                name = f.stem
                index[name] = f"[[{name}]]"

        # Scan 4-Questions/
        questions_dir = self.vault / "4-Questions"
        if questions_dir.exists():
            for f in questions_dir.glob("*.md"):
                if "INDEX" in f.name or "TEMPLATE" in f.name:
                    continue
                name = f.stem
                index[name] = f"[[{name}]]"

        return index

    def build_links(self, text: str) -> str:
        """Replace known entity names with [[wikilinks]]."""
        # Sort by key length descending to match longer names first
        for name in sorted(self.link_index.keys(), key=len, reverse=True):
            if name in text:
                wikilink = self.link_index[name]
                # Only replace if not already inside a wikilink
                if f"[[{name}]]" not in text:
                    text = text.replace(name, wikilink)
        return text

    def process_file(self, filepath: Path) -> dict:
        """Process a single markdown file, injecting wikilinks."""
        if not filepath.exists():
            return {"file": str(filepath), "links_added": 0}

        original = filepath.read_text(encoding="utf-8")
        modified = self.build_links(original)

        if modified != original:
            filepath.write_text(modified, encoding="utf-8")
            # Count how many links were added
            import re
            old_count = len(re.findall(r"\[\[[^\]]+\]\]", original))
            new_count = len(re.findall(r"\[\[[^\]]+\]\]", modified))
            return {"file": str(filepath), "links_added": new_count - old_count}

        return {"file": str(filepath), "links_added": 0}

    def process_vault(self) -> dict:
        """Process all eligible files in the vault."""
        results = []
        for folder in ["6-Reviews", "0-Inbox", "1-Experiences"]:
            folder_path = self.vault / folder
            if not folder_path.exists():
                continue
            for f in folder_path.glob("*.md"):
                r = self.process_file(f)
                results.append(r)

        total_links = sum(r["links_added"] for r in results)
        return {"files_processed": len(results), "total_links_added": total_links, "details": results}


def main():
    parser = argparse.ArgumentParser(description="Build Obsidian wikilinks in MindOS vault")
    parser.add_argument("vault_root", nargs="?", default=".")
    args = parser.parse_args()

    vault = Path(args.vault_root)
    try:
        builder = LinkBuilder(vault)
        result = builder.process_vault()
        print(json.dumps({"success": True, **result}, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
