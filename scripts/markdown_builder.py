#!/usr/bin/env python3
"""
MindOS markdown_builder.py — Obsidian node Markdown generator.

Builds typed, linkable Markdown files from structured data.
Uses frontmatter.py for consistent YAML headers.

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.frontmatter import (
    build_frontmatter,
    book_frontmatter,
    reading_review_frontmatter,
    pattern_frontmatter,
    goal_frontmatter,
    memory_frontmatter,
)


class MarkdownBuilder:
    """Build Obsidian-ready markdown files with typed frontmatter."""

    def build_book(self, title: str, author: str = "", topics: list[str] | None = None, highlights: list[str] | None = None) -> str:
        fm = book_frontmatter(title, author=author, topics=topics)
        body_parts = [fm, f"# {title}\n"]
        if highlights:
            body_parts.append("## 我的标记\n")
            for h in highlights[:10]:
                body_parts.append(f"> {h}\n")
        body_parts.append("## MindOS 分析\n\n<!-- Claude: 这本书与你的知识网络的关联 -->\n")
        return "\n".join(body_parts)

    def build_reading_review(
        self,
        date_str: str,
        layer1: str = "",
        layer2: str = "",
        layer3: str = "",
        reflection: str = "",
        evidence: list[dict] | None = None,
    ) -> str:
        fm = reading_review_frontmatter(date_str)
        parts = [fm, f"# {date_str} 阅读分析\n"]

        if layer1:
            parts.append(f"## Layer 1 — 事实\n\n{layer1}\n")
        if layer2:
            parts.append(f"## Layer 2 — 关联\n\n{layer2}\n")
        if layer3:
            parts.append(f"## Layer 3 — 叙事\n\n{layer3}\n")
        if evidence:
            parts.append("## Evidence\n\n")
            for e in evidence:
                parts.append(f"- [{e.get('source', '?')}] {e.get('fact', '')}\n")
        if reflection:
            parts.append(f"## 反思\n\n{reflection}\n")

        return "\n".join(parts)

    def build_pattern(self, name: str, description: str = "", evidence_refs: list[str] | None = None) -> str:
        fm = pattern_frontmatter(name, evidence_count=len(evidence_refs) if evidence_refs else 0)
        parts = [fm, f"# {name}\n"]
        if description:
            parts.append(f"## 描述\n\n{description}\n")
        if evidence_refs:
            parts.append("## 证据\n")
            for ref in evidence_refs:
                parts.append(f"- {ref}\n")
        parts.append("\n## 我的判断\n\n<!-- 这个模式准确吗？ -->\n")
        return "\n".join(parts)

    def build_goal(self, area: str, why: str = "", milestones: list[str] | None = None) -> str:
        fm = goal_frontmatter(area)
        parts = [fm, f"# {area}\n"]
        if why:
            parts.append(f"## 为什么重要\n\n{why}\n")
        if milestones:
            parts.append("## 关键里程碑\n")
            for m in milestones:
                parts.append(f"- [ ] {m}\n")
        return "\n".join(parts)

    def build_memory(self, title: str, narrative: str = "", score: float = 0.0) -> str:
        fm = memory_frontmatter(title, score=score)
        parts = [fm, f"# {title}\n"]
        if narrative:
            parts.append(narrative)
        return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Build Obsidian markdown nodes")
    parser.add_argument("--type", choices=["book", "review", "pattern", "goal", "memory"], required=True, help="Node type")
    parser.add_argument("--input", help="JSON input file with node data")
    parser.add_argument("--output", help="Output markdown file path")
    args = parser.parse_args()

    builder = MarkdownBuilder()

    try:
        data = {}
        if args.input:
            data = json.loads(Path(args.input).read_text(encoding="utf-8"))

        if args.type == "book":
            result = builder.build_book(
                title=data.get("title", "Untitled"),
                author=data.get("author", ""),
                topics=data.get("topics"),
                highlights=data.get("highlights"),
            )
        elif args.type == "review":
            result = builder.build_reading_review(
                date_str=data.get("date", datetime.now().strftime("%Y-%m-%d")),
                layer1=data.get("layer1", ""),
                layer2=data.get("layer2", ""),
                layer3=data.get("layer3", ""),
                reflection=data.get("reflection", ""),
                evidence=data.get("evidence"),
            )
        elif args.type == "pattern":
            result = builder.build_pattern(
                name=data.get("name", "New Pattern"),
                description=data.get("description", ""),
                evidence_refs=data.get("evidence_refs"),
            )
        elif args.type == "goal":
            result = builder.build_goal(
                area=data.get("area", "New Goal"),
                why=data.get("why", ""),
                milestones=data.get("milestones"),
            )
        elif args.type == "memory":
            result = builder.build_memory(
                title=data.get("title", "Memory"),
                narrative=data.get("narrative", ""),
                score=data.get("score", 0.0),
            )

        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
            print(json.dumps({"success": True, "path": args.output, "type": args.type}, ensure_ascii=False))
        else:
            print(result)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
