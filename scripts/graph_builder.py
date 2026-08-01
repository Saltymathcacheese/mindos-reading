#!/usr/bin/env python3
"""
MindOS graph_builder.py — Build knowledge graph from vault nodes.

Scans vault for typed nodes (books, concepts, patterns, goals)
and builds a structured graph with typed edges.

Output: 7-System/knowledge_graph.json

Usage: python scripts/graph_builder.py [vault_root]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


class GraphBuilder:
    def __init__(self, vault: Path):
        self.vault = vault

    def build(self) -> dict:
        nodes: dict[str, dict] = {}
        edges: list[dict] = []

        for f in self.vault.rglob("*.md"):
            if ".obsidian" in str(f) or "Templates" in str(f) or "TEMPLATE" in f.name:
                continue

            try:
                text = f.read_text(encoding="utf-8")
                fm = self._parse_frontmatter(text)
                node_type = fm.get("type", "note")
                node_id = fm.get("id", f.stem)

                nodes[node_id] = {
                    "name": f.stem,
                    "type": node_type,
                    "path": str(f.relative_to(self.vault)),
                    "date": fm.get("date", fm.get("created", "")),
                    "tags": fm.get("tags", []),
                }

                # Extract typed relations from frontmatter
                relations = fm.get("relations", fm.get("related", []))
                if isinstance(relations, list):
                    for rel in relations:
                        if isinstance(rel, dict):
                            target = rel.get("target", "").strip("[[]] ")
                            rel_type = rel.get("relation", "associated_with")
                            if target:
                                edges.append({
                                    "from": node_id,
                                    "to": target,
                                    "relation": rel_type,
                                })

                # Extract raw [[wikilinks]] as associated_with edges
                wikilinks = re.findall(r"\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]", text)
                for link in wikilinks:
                    clean = link.split("#")[0].split("|")[0].strip()
                    if clean and clean != node_id:
                        edges.append({
                            "from": node_id,
                            "to": clean,
                            "relation": "associated_with",
                        })

            except Exception:
                continue

        # Deduplicate edges
        seen = set()
        unique_edges = []
        for e in edges:
            key = (e["from"], e["to"], e["relation"])
            if key not in seen:
                seen.add(key)
                unique_edges.append(e)

        # Count node types
        type_counts: dict[str, int] = {}
        for n in nodes.values():
            t = n["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        # Count relation types
        rel_counts: dict[str, int] = {}
        for e in unique_edges:
            r = e["relation"]
            rel_counts[r] = rel_counts.get(r, 0) + 1

        return {
            "nodes": len(nodes),
            "edges": len(unique_edges),
            "node_types": type_counts,
            "relation_types": rel_counts,
            "graph": {
                "nodes": list(nodes.values()),
                "edges": unique_edges,
            },
        }

    def _parse_frontmatter(self, text: str) -> dict:
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
                    items = v[1:-1].split(",")
                    v = [x.strip().strip('"').strip("'") for x in items if x.strip()]
                fm[k.strip()] = v
        return fm


def main():
    parser = argparse.ArgumentParser(description="Build MindOS knowledge graph")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--output", default=None, help="Output path (default: 7-System/knowledge_graph.json)")
    args = parser.parse_args()

    vault = Path(args.vault_root)
    try:
        builder = GraphBuilder(vault)
        result = builder.build()

        output_path = Path(args.output) if args.output else (vault / "7-System" / "knowledge_graph.json")
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        print(json.dumps({
            "success": True,
            "nodes": result["nodes"],
            "edges": result["edges"],
            "path": str(output_path),
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
