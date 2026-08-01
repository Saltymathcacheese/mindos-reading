#!/usr/bin/env python3
"""
MindOS concept_extractor.py — Extract recurring concepts from reading highlights.

Scans weread data and existing knowledge nodes to identify candidate concepts
that appear across multiple books or notes. Outputs candidates for Claude to validate.

Does NOT create concepts automatically — only surfaces candidates with evidence.

Usage: python scripts/concept_extractor.py [vault_root]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# ── Concept seed patterns — high-signal phrases that suggest a concept ──
CONCEPT_PATTERNS = [
    r"([一-鿿]{2,6})(?:偏差|效应|模型|理论|机制|原则|策略|框架|模式|系统|推理|判断)",
    r"(如何|为什么|什么是)([一-鿿]{2,8})",
]

# ── Stopwords to filter out noise ──
STOP_CONCEPTS = {
    "一个", "这种", "那个", "自己", "可以", "不是", "因为", "所以", "但是", "如果",
    "他们", "我们", "什么", "怎么", "没有", "已经", "还是", "这个", "这些",
}


class ConceptExtractor:
    def __init__(self, vault: Path):
        self.vault = vault

    def extract_from_highlights(self) -> list[dict]:
        """Extract candidate concepts from weread highlight data."""
        weread_path = self.vault / "7-System" / "raw_we_read.json"
        if not weread_path.exists():
            return []

        data = json.loads(weread_path.read_text(encoding="utf-8"))
        highlights_data = data.get("data", {}).get("highlights_top3", [])

        phrases: Counter = Counter()
        book_sources: dict[str, set[str]] = {}

        for book in highlights_data:
            book_name = book.get("book", "")
            for h in book.get("highlights", []):
                text = h.get("text", "")
                for pattern in CONCEPT_PATTERNS:
                    for match in re.finditer(pattern, text):
                        concept = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                        concept = concept.strip()
                        if concept not in STOP_CONCEPTS and len(concept) >= 2:
                            phrases[concept] += 1
                            if concept not in book_sources:
                                book_sources[concept] = set()
                            book_sources[concept].add(book_name)

        # Filter: concept must appear ≥2 times or across ≥2 books
        candidates = []
        for concept, count in phrases.most_common(30):
            sources = book_sources.get(concept, set())
            if count >= 2 or len(sources) >= 2:
                candidates.append({
                    "concept": concept,
                    "frequency": count,
                    "sources": list(sources),
                    "confidence": "L1" if count >= 3 else "L0",
                })

        return candidates

    def check_existing(self, candidates: list[dict]) -> list[dict]:
        """Mark candidates that already exist as concept nodes."""
        concepts_dir = self.vault / "2-Knowledge" / "Concepts"
        existing = set()
        if concepts_dir.exists():
            for f in concepts_dir.glob("*.md"):
                existing.add(f.stem)

        for c in candidates:
            c["already_exists"] = c["concept"] in existing

        return candidates

    def run(self) -> dict:
        candidates = self.extract_from_highlights()
        candidates = self.check_existing(candidates)
        new = [c for c in candidates if not c["already_exists"]]
        return {
            "total_candidates": len(candidates),
            "new_candidates": len(new),
            "existing": len(candidates) - len(new),
            "candidates": new[:10],  # top 10 for Claude to review
        }


def main():
    parser = argparse.ArgumentParser(description="Extract concept candidates from reading data")
    parser.add_argument("vault_root", nargs="?", default=".")
    args = parser.parse_args()

    try:
        extractor = ConceptExtractor(Path(args.vault_root))
        result = extractor.run()
        print(json.dumps({"success": True, **result}, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
