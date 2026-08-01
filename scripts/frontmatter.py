#!/usr/bin/env python3
"""
MindOS frontmatter.py — Typed frontmatter builder for Obsidian nodes.

Generates consistent YAML frontmatter for all 6 MindOS node types.
Each node gets: id, type, created, updated, source, confidence, relations, status.

Python >= 3.11
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def build_frontmatter(
    node_type: str,
    *,
    title: str = "",
    created: str | None = None,
    source: list[str] | None = None,
    confidence: str = "L1",
    relations: list[dict[str, str]] | None = None,
    tags: list[str] | None = None,
    status: str = "active",
    extra: dict[str, Any] | None = None,
) -> str:
    """Build YAML frontmatter string for a MindOS node.

    node_type: book | reading-analysis | diary | pattern | goal | memory
    """
    today = datetime.now().strftime("%Y-%m-%d")
    created = created or today
    node_id = f"{node_type}-{title.replace(' ', '-')}-{today.replace('-', '')}"

    lines = ["---"]
    lines.append(f"id: {node_id}")
    lines.append(f"type: {node_type}")
    lines.append(f"title: \"{title}\"")
    lines.append(f"created: {created}")
    lines.append(f"updated: {today}")

    if source:
        lines.append("source:")
        for s in source:
            lines.append(f"  - {s}")
    else:
        lines.append("source: []")

    lines.append(f"confidence: {confidence}")

    if relations:
        lines.append("relations:")
        for r in relations:
            target = r.get("target", "")
            relation = r.get("relation", "related")
            lines.append(f"  - target: \"[[{target}]]\"")
            lines.append(f"    relation: {relation}")
    else:
        lines.append("relations: []")

    if tags:
        lines.append("tags:")
        for t in tags:
            lines.append(f"  - {t}")

    lines.append(f"status: {status}")

    if extra:
        for k, v in extra.items():
            if isinstance(v, list):
                lines.append(f"{k}:")
                for item in v:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{k}: {v}")

    lines.append("---")
    return "\n".join(lines)


# ── Type-specific builders ──

def book_frontmatter(title: str, author: str = "", topics: list[str] | None = None, **kwargs: Any) -> str:
    extra = kwargs.pop("extra", {}) if "extra" in kwargs else {}
    if author:
        extra["author"] = author
    if topics:
        extra["topics"] = topics
    return build_frontmatter("book", title=title, source=["WeRead"], tags=topics, extra=extra, **kwargs)


def reading_review_frontmatter(date_str: str, **kwargs: Any) -> str:
    return build_frontmatter(
        "reading-analysis",
        title=f"{date_str} 阅读分析",
        created=date_str,
        source=["WeRead", "Obsidian"],
        tags=["reading", "analysis"],
        **kwargs,
    )


def pattern_frontmatter(name: str, evidence_count: int = 0, **kwargs: Any) -> str:
    return build_frontmatter(
        "pattern",
        title=name,
        source=["MindOS"],
        tags=["pattern"],
        extra={"evidence_count": evidence_count},
        **kwargs,
    )


def goal_frontmatter(area: str, priority: int = 3, **kwargs: Any) -> str:
    return build_frontmatter(
        "goal",
        title=area,
        source=[],
        tags=["goal"],
        extra={"priority": priority},
        **kwargs,
    )


def memory_frontmatter(title: str, score: float = 0.0, **kwargs: Any) -> str:
    return build_frontmatter(
        "memory",
        title=title,
        source=["MindOS"],
        tags=["memory"],
        extra={"memory_score": score},
        **kwargs,
    )
