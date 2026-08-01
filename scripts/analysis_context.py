#!/usr/bin/env python3
"""
MindOS analysis_context.py — Cognitive Evidence Package Builder.

Reads raw data from multiple sources and assembles a unified Evidence Bundle
for the cognitive analysis layer (Claude + references/).

This script does NOT perform cognitive reasoning.
It only structures facts for the reasoning layer to consume.

Inputs:
    - 7-System/raw_we_read.json (from weread_fetch.py)
    - 1-Experiences/*.md (diary entries, last 30 days)
    - 7-System/analysis_state.yaml (current state)

Output:
    analysis_context.json → consumed by report_generator + Claude

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

logger = logging.getLogger("mindos.context")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# =========================
# Data Loaders
# =========================
def load_weread_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load weread JSON: %s", e)
        return None


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse YAML frontmatter from markdown, stripping inline comments."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    yaml = YAML()
    try:
        data = yaml.load(parts[1].strip())
        if not isinstance(data, dict):
            return {}
        # Clean values
        cleaned: dict[str, Any] = {}
        for k, v in data.items():
            if isinstance(v, str):
                # Strip inline YAML comments
                if "#" in v:
                    v = v.split("#", 1)[0].strip()
                # Unresolved template vars → None
                if v.startswith("{{") and v.endswith("}}"):
                    v = None
            elif not isinstance(v, (int, float, bool, list, type(None))):
                # ruamel.yaml artefact (CommentedMap etc) → treat as absent
                v = None
            cleaned[k] = v
        return cleaned
    except Exception:
        return {}


def load_diary_entries(experiences_dir: Path, days: int = 30) -> list[dict]:
    """Load diary entries from the past N days."""
    if not experiences_dir.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    entries: list[dict] = []

    for f in sorted(experiences_dir.glob("*.md"), reverse=True):
        try:
            text = f.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            content = text.split("---", 2)[-1] if text.startswith("---") else text

            # Check date in filename or frontmatter
            date_str = fm.get("date") or f.stem.replace("日记", "").replace(".md", "")
            try:
                entry_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except ValueError:
                try:
                    entry_date = datetime.strptime(date_str[:10], "%Y.%m.%d")
                except ValueError:
                    entry_date = datetime.fromtimestamp(f.stat().st_mtime)

            if entry_date < cutoff:
                break  # files are sorted reverse-chronological

            entries.append({
                "file": f.name,
                "date": entry_date.strftime("%Y-%m-%d"),
                "mood": fm.get("mood", ""),
                "energy": fm.get("energy", ""),
                "content_preview": content.strip()[:200],
                "word_count": len(content.split()),
            })
        except Exception as e:
            logger.debug("Skipping %s: %s", f.name, e)
            continue

    return entries


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    yaml = YAML()
    with path.open("r", encoding="utf-8") as f:
        return yaml.load(f) or {}


# =========================
# Evidence Bundle Builder
# =========================
def extract_reading_evidence(weread: dict | None) -> dict:
    """Extract structured reading facts from weread pipeline output."""
    if not weread or not weread.get("success"):
        return {"available": False, "reason": "No weread data"}

    data = weread.get("data", weread)
    stats = data.get("stats", {})
    rt = stats.get("reading_time", {})
    prev = data.get("prev_stats") or {}
    prev_rt = prev.get("reading_time", {}) if prev else {}

    # Current vs previous trend
    current_seconds = rt.get("total_seconds", 0)
    prev_seconds = prev_rt.get("total_seconds", 0)
    if prev_seconds > 0:
        pct = round((current_seconds - prev_seconds) / prev_seconds * 100, 1)
        trend = "up" if pct > 5 else "down" if pct < -5 else "stable"
    else:
        pct = None
        trend = "baseline"

    # Books
    books = data.get("books_top10", [])
    top_books = [
        {
            "title": b.get("title", "?"),
            "author": b.get("author", "?"),
            "categories": b.get("categories", []),
            "total_notes": b.get("total_notes", 0),
            "notes_breakdown": {
                "highlights": b.get("note_count", 0),
                "thoughts": b.get("review_count", 0),
                "bookmarks": b.get("bookmark_count", 0),
            },
            "reading_status": "finished" if b.get("marked_status") == 4 else "reading",
        }
        for b in books
    ]

    # Categories
    prefer_categories = [
        {"name": c.get("categoryTitle", c.get("title", "")), "reading_time_seconds": c.get("readingTime", c.get("val", 0))}
        for c in stats.get("prefer_categories", [])
    ]

    # Highlights
    highlights = data.get("highlights_top3", [])

    # Shelf
    shelf = data.get("shelf", {})
    archives = shelf.get("archives", [])

    return {
        "available": True,
        "period": {
            "current_month_hours": round(current_seconds / 3600, 1),
            "previous_month_hours": round(prev_seconds / 3600, 1),
            "change_pct": pct,
            "trend": trend,
            "read_days": stats.get("read_days", 0),
        },
        "top_books": top_books,
        "total_books_with_notes": data.get("books_total", 0),
        "total_notes_all_time": data.get("total_notes_all_books", 0),
        "prefer_categories": prefer_categories,
        "highlights_top3": highlights,
        "shelf": {
            "total_items": shelf.get("total_items", 0),
            "booklists": archives,
        },
    }


def extract_diary_evidence(entries: list[dict]) -> dict:
    """Extract structured diary facts."""
    if not entries:
        return {"available": False, "entry_count": 0}

    moods = [e.get("mood") for e in entries if e.get("mood")]
    mood_counts: dict[str, int] = {}
    for m in moods:
        mood_counts[m] = mood_counts.get(m, 0) + 1

    return {
        "available": True,
        "entry_count": len(entries),
        "date_range": {
            "from": entries[-1]["date"] if entries else None,
            "to": entries[0]["date"] if entries else None,
        },
        "mood_distribution": mood_counts,
        "avg_word_count": round(sum(e.get("word_count", 0) for e in entries) / max(len(entries), 1)),
    }


def extract_runtime_evidence(state: dict, preflight: dict | None) -> dict:
    """Extract current system state facts."""
    return {
        "mode": preflight.get("mode", "V0.1") if preflight else "V0.1",
        "diary_entries_total": preflight.get("diary_count", 0) if preflight else 0,
        "patterns_confirmed": preflight.get("patterns_confirmed", 0) if preflight else 0,
        "safe_mode": preflight.get("safe_mode", False) if preflight else False,
        "last_analysis": state.get("last_analysis", {}).get("date"),
        "session_count": state.get("metrics", {}).get("session_count", 0),
    }


def extract_scholar_context(state: dict) -> dict:
    """Load scholar profile from analysis_state references."""
    scholar = state.get("scholar_profile") or {}
    return {
        "field": scholar.get("field", "口腔医学"),
        "subfield": scholar.get("subfield", ""),
        "stage": scholar.get("stage", ""),
    }


# =========================
# Bundle Assembly
# =========================
def build_context(vault_root: Path) -> dict:
    """Assemble the full Evidence Bundle."""
    # Data files
    weread_path = vault_root / "7-System" / "raw_we_read.json"
    state_path = vault_root / "7-System" / "analysis_state.yaml"
    experiences_dir = vault_root / "1-Experiences"

    # Load
    weread = load_weread_json(weread_path)
    state = load_state(state_path)
    diary_entries = load_diary_entries(experiences_dir)

    # Build evidence layers
    reading = extract_reading_evidence(weread)
    diary = extract_diary_evidence(diary_entries)
    runtime = extract_runtime_evidence(state, None)
    scholar = extract_scholar_context(state)

    # Available cognitive modules
    available_modules = ["analysis-pipeline", "scholar-module", "confidence-system"]
    if runtime["mode"] in ("V0.2", "V0.3"):
        available_modules.append("pattern-engine")
        available_modules.append("interaction-rules")
    if runtime["mode"] == "V0.3":
        available_modules.append("hypothesis-framework")
        available_modules.append("action-layer")
        available_modules.append("memory-compression")

    return {
        "generated_at": datetime.now().isoformat(),
        "version": "2.3",
        "runtime": runtime,
        "scholar": scholar,
        "available_modules": available_modules,
        "evidence": {
            "reading": reading,
            "diary": diary,
        },
    }


# =========================
# CLI
# =========================
def main():
    parser = argparse.ArgumentParser(description="Build MindOS Evidence Bundle")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--output", default=None, help="Output path (default: 7-System/analysis_context.json)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    vault = Path(args.vault_root)

    try:
        bundle = build_context(vault)
        output_path = Path(args.output) if args.output else (vault / "7-System" / "analysis_context.json")
        output_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"success": True, "path": str(output_path), "mode": bundle["runtime"]["mode"]}, ensure_ascii=False))
    except Exception as e:
        logger.exception("Context build failed")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
