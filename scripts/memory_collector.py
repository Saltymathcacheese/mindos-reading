#!/usr/bin/env python3
"""Memory collector — gather content from 6-Reviews, 1-Experiences, 3-Patterns for compression."""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


class MemoryCollector:
    def __init__(self, vault: Path):
        self.vault = vault

    def _collect_folder(self, folder: str, max_files: int = 50, days: int = 90) -> list[dict]:
        path = self.vault / folder
        if not path.exists():
            return []

        cutoff = datetime.now() - timedelta(days=days)
        items = []

        for f in sorted(path.rglob("*.md"), reverse=True):
            if len(items) >= max_files:
                break
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime < cutoff:
                    continue
                items.append({
                    "file": str(f.relative_to(self.vault)),
                    "folder": folder,
                    "mtime": mtime.isoformat(),
                    "content": f.read_text(encoding="utf-8")[:2000],  # cap per file
                })
            except Exception:
                continue
        return items

    def collect(self) -> dict:
        return {
            "reviews": self._collect_folder("6-Reviews", max_files=20),
            "diary": self._collect_folder("1-Experiences", max_files=30),
            "patterns": self._collect_folder("3-Patterns", max_files=10),
        }


def main():
    parser = argparse.ArgumentParser(description="Collect MindOS memory candidates")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--output", default=None, help="Output path (default: 7-System/memory_candidates.json)")
    args = parser.parse_args()

    vault = Path(args.vault_root)
    try:
        collector = MemoryCollector(vault)
        result = collector.collect()

        output_path = Path(args.output) if args.output else (vault / "7-System" / "memory_candidates.json")
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        total = sum(len(v) for v in result.values())
        print(json.dumps({"success": True, "path": str(output_path), "total_candidates": total}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
