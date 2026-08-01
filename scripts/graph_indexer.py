#!/usr/bin/env python3
"""
MindOS graph_indexer.py — Build Obsidian graph statistics.

Counts nodes, edges, and key metrics to understand how the vault's
knowledge graph is evolving over time.

Usage: python scripts/graph_indexer.py [vault_root]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


class GraphIndexer:
    def __init__(self, vault: Path):
        self.vault = vault

    def index(self) -> dict:
        nodes: dict[str, dict] = {}
        edges: list[tuple[str, str, str]] = []  # (from, to, context)

        for f in self.vault.rglob("*.md"):
            if ".obsidian" in str(f) or "Templates" in str(f) or "TEMPLATE" in f.name:
                continue

            try:
                text = f.read_text(encoding="utf-8")
                fm = self._extract_frontmatter(text)
                node_type = fm.get("type", "note")

                nodes[f.stem] = {
                    "path": str(f.relative_to(self.vault)),
                    "type": node_type,
                    "date": fm.get("date", ""),
                    "tags": fm.get("tags", []),
                }

                # Extract outgoing [[wikilinks]]
                links = re.findall(r"\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]", text)
                for link in links:
                    clean = link.split("#")[0].split("|")[0].strip()
                    if clean:
                        edges.append((f.stem, clean, node_type))

            except Exception:
                continue

        # Count by type
        type_counts: dict[str, int] = {}
        for n in nodes.values():
            t = n["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": type_counts,
            "densest_nodes": self._top_connected(nodes, edges, top_n=5),
        }

    def _extract_frontmatter(self, text: str) -> dict:
        if not text.startswith("---"):
            return {}
        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}
        fm: dict = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                v = v.strip().strip('"').strip("'")
                if v.startswith("[") and v.endswith("]"):
                    v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
                fm[k.strip()] = v
        return fm

    def _top_connected(self, nodes: dict, edges: list, top_n: int = 5) -> list[dict]:
        out_count: dict[str, int] = {}
        in_count: dict[str, int] = {}
        for src, dst, _ in edges:
            out_count[src] = out_count.get(src, 0) + 1
            in_count[dst] = in_count.get(dst, 0) + 1

        all_nodes = set(out_count) | set(in_count)
        ranked = sorted(all_nodes, key=lambda n: out_count.get(n, 0) + in_count.get(n, 0), reverse=True)
        return [
            {"node": n, "outgoing": out_count.get(n, 0), "incoming": in_count.get(n, 0),
             "type": nodes.get(n, {}).get("type", "unknown")}
            for n in ranked[:top_n]
        ]


def main():
    parser = argparse.ArgumentParser(description="Index MindOS vault graph structure")
    parser.add_argument("vault_root", nargs="?", default=".")
    args = parser.parse_args()

    try:
        indexer = GraphIndexer(Path(args.vault_root))
        result = indexer.index()
        print(json.dumps({"success": True, **result}, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
