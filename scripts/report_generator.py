#!/usr/bin/env python3
"""
MindOS report_generator.py — Markdown report scaffold from Evidence Bundle.

Reads analysis_context.json and produces a structured markdown report
with facts populated, interpretation sections left for Claude to fill.

This script does NOT generate cognitive insights.
It populates the Surface layer (Layer 1) with data.
Layers 2-3 are filled by Claude using references/.

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("mindos.report")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# =========================
# Template Renderer
# =========================
def render_reading_section(reading: dict) -> str:
    """Populate the 📊 阅读统计 section with facts."""
    if not reading.get("available"):
        return "本月暂无微信读书数据。"

    period = reading["period"]
    trend_arrow = "↑" if period["trend"] == "up" else "↓" if period["trend"] == "down" else "→"
    change_str = f"{period['change_pct']:+.1f}%" if period["change_pct"] is not None else "无上月对比数据"

    lines = [
        "## 📊 阅读统计\n",
        "| 指标 | 数值 | 趋势 |",
        "|------|------|------|",
        f"| 本月阅读时长 | {period['current_month_hours']:.1f} 小时 | {trend_arrow} {change_str} |",
        f"| 阅读天数 | {period['read_days']} 天 | — |",
        f"| 笔记库存总数 | {reading.get('total_notes_all_time', 0)} 条（来自 {reading.get('total_books_with_notes', 0)} 本书） | — |",
    ]

    # Top books table
    top = reading.get("top_books", [])
    if top:
        lines.append("\n### 📖 笔记最多的书\n")
        lines.append("| 书 | 类别 | 划线 | 想法 | 书签 | 总笔记 | 状态 |")
        lines.append("|---|------|------|------|------|--------|------|")
        for b in top[:10]:
            nb = b["notes_breakdown"]
            lines.append(
                f"| {b['title']} | {', '.join(b['categories'][:2])} | "
                f"{nb['highlights']} | {nb['thoughts']} | {nb['bookmarks']} | "
                f"{b['total_notes']} | {b['reading_status']} |"
            )

    # Shelf booklists
    booklists = reading.get("shelf", {}).get("booklists", [])
    if booklists:
        lines.append("\n### 🏷 书架组织\n")
        bl_names = [f"{bl['name']}（{bl['book_count']}本）" for bl in booklists[:8]]
        lines.append(f"你的书单：{' · '.join(bl_names)}\n")

    # Highlights
    highlights = reading.get("highlights_top3", [])
    if highlights:
        lines.append("\n### ✍️ 笔记摘录（Top 3 书籍）\n")
        for h in highlights[:3]:
            lines.append(f"\n**《{h.get('book', '?')}》**")
            for item in h.get("highlights", [])[:5]:
                text = item.get("text", "")
                if text:
                    lines.append(f"> {text}\n")

    return "\n".join(lines)


def render_identity_section(reading: dict) -> str:
    """Identity Router v3.1 — determine which identities are active this month."""
    books = reading.get("top_books", [])
    identities: dict[str, list[str]] = {}

    for b in books:
        cats = b.get("categories", [])
        identity = _route_identity(cats)
        if identity not in identities:
            identities[identity] = []
        identities[identity].append(b.get("title", "?"))

    active_list = []
    inactive_list = []
    all_identities = ["Professional", "Learner", "Explorer", "Self-Understanding", "Restorative"]
    for ident in all_identities:
        if ident in identities:
            active_list.append(f"- **{ident}** — 已激活（{'、'.join(identities[ident][:2])}）")
        else:
            inactive_list.append(f"- **{ident}** — 本月无明显信号")

    return (
        f"\n## 🪪 身份感知\n\n"
        f"<!-- 见 references/identity-layer.md -->\n\n"
        + "\n".join(active_list) +
        f"\n" + "\n".join(inactive_list) +
        f"\n"
    )


def _route_identity(categories: list[str]) -> str:
    """Map weread categories to MindOS identity dimensions."""
    for c in categories:
        cl = c.lower()
        if any(w in cl for w in ["医学", "健康-医学", "医疗"]):
            return "Professional"
        if any(w in cl for w in ["心理-认知", "认知", "科学"]):
            return "Explorer"
        if any(w in cl for w in ["心理-亲密", "心理-社会", "心理-应用", "情感", "自我", "成长-人生"]):
            return "Self-Understanding"
        if any(w in cl for w in ["教育", "成长-认知", "管理", "技能"]):
            return "Learner"
        if any(w in cl for w in ["文学", "艺术", "漫画", "小说", "摄影", "散文", "诗词"]):
            return "Restorative"
    return "Explorer"  # default: intellectual curiosity


def render_scholar_section(scholar: dict, reading: dict) -> str:
    """Scholar section v2: domain-first, tiered lens."""
    # Extract domains from reading data
    books = reading.get("top_books", [])
    domains: dict[str, list[str]] = {}
    for b in books:
        cats = b.get("categories", [])
        for c in cats:
            d = _classify_domain(c)
            if d not in domains:
                domains[d] = []
            domains[d].append(b.get("title", "?"))

    domain_lines = []
    for d_name, d_books in domains.items():
        domain_lines.append(f"- **{d_name}**：{'、'.join(d_books[:3])}")

    return (
        f"\n## 🧠 阅读领域分布\n\n"
        f"<!-- 根据 references/reading-taxonomy.md 六域分类 -->\n\n"
        + "\n".join(domain_lines) +
        f"\n\n## 🌱 个人成长视角（Tier 1 — 始终启用）\n\n"
        f"<!-- Claude: 见 references/scholar-module.md Tier 1 -->\n\n"
        f"- **学习效能** — <!-- Claude fill: 学习方法论、自我调节信号 -->\n"
        f"- **认知广度** — <!-- Claude fill: 领域分布、兴趣迁移 -->\n"
        f"- **自我理解** — <!-- Claude fill: 情绪、关系、价值探索 -->\n"
        f"\n## 🩺 专业成长视角（Tier 2 — 仅当证据支持时启用）\n\n"
        f"<!-- Claude: 仅当满足激活条件时才填写。无信号时写'本月无明显X信号' -->\n\n"
        f"- **职业认同** — <!-- Claude fill -->\n"
        f"- **临床思维** — <!-- Claude fill -->\n"
        f"- **科研素养** — <!-- Claude fill -->\n"
    )


def _classify_domain(category: str) -> str:
    """Classify a weread category into a MindOS reading domain."""
    c = category.lower()
    if any(w in c for w in ["医学", "健康", "医疗"]):
        return "专业成长"
    if any(w in c for w in ["心理", "认知", "个人成长", "教育"]):
        return "通识认知"
    if any(w in c for w in ["历史", "哲学", "艺术", "文学", "文化"]):
        return "人文素养"
    if any(w in c for w in ["亲密", "情感", "自我"]):
        return "自我理解"
    if any(w in c for w in ["漫画", "小说", "摄影", "旅游", "生活"]):
        return "兴趣娱乐"
    if any(w in c for w in ["计算机", "科学", "技术", "技能"]):
        return "信息获取"
    return "其他"


def render_narrative_section() -> str:
    """Layer 3 placeholder for Claude."""
    return (
        "\n## 💭 本月叙事\n\n"
        "<!-- Claude: 见 references/analysis-pipeline.md Layer 3 -->\n\n"
        "**核心叙事：** <!-- Claude: 1-2 句话，这些书加在一起在找什么？ -->\n\n"
        "**方向变化：** <!-- Claude: 思维在往哪里移动？ -->\n\n"
        "**一个值得注意的信号：** <!-- Claude: 如果有一个明显变化，在这里指出。没有则写'本月无显著异常信号' -->\n"
    )


def render_report(bundle: dict) -> str:
    """Assemble full report markdown."""
    today = datetime.now().strftime("%Y-%m-%d")
    evidence = bundle.get("evidence", {})
    reading = evidence.get("reading", {})
    diary = evidence.get("diary", {})
    runtime = bundle.get("runtime", {})
    scholar = bundle.get("scholar", {})

    sections = [
        f"---\n"
        f"id: review-{today.replace('-', '')}-reading\n"
        f"type: reading-analysis\n"
        f"date: {today}\n"
        f"period: \"30天\"\n"
        f"tags: [reading, analysis]\n"
        f"data_source: \"微信读书 API\"\n"
        f"mode: {runtime.get('mode', 'V0.1')}\n"
        f"confidence_note: \"所有解释性结论待 Claude 标注置信度 (L0-L4)\"\n"
        f"source:\n"
        f"  - WeRead\n"
        f"  - Obsidian\n"
        f"related: []\n"
        f"status: active\n"
        f"---\n",
        f"# {today} 阅读分析\n",
        render_reading_section(reading),
    ]

    if diary.get("available"):
        sections.append(
            f"\n## 📝 日记概览\n\n"
            f"本月日记：{diary['entry_count']} 篇 | "
            f"平均字数：{diary['avg_word_count']} 字 | "
            f"情绪分布：{diary.get('mood_distribution', {})}\n"
        )

    sections.append(render_identity_section(reading))
    sections.append(render_scholar_section(scholar, reading))
    sections.append(render_narrative_section())

    sections.append("\n---\n*报告框架由 MindOS v2.3 生成。认知分析由 Claude 根据 references/ 完成。*")

    return "\n".join(sections)


# =========================
# CLI
# =========================
def main():
    parser = argparse.ArgumentParser(description="Generate MindOS reading report scaffold")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--output", default=None, help="Output path (default: 6-Reviews/YYYY-MM-DD-阅读分析.md)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    vault = Path(args.vault_root)
    context_path = vault / "7-System" / "analysis_context.json"

    try:
        if not context_path.exists():
            print(json.dumps({"success": False, "error": "analysis_context.json not found — run analysis_context.py first"}))
            sys.exit(1)

        bundle = json.loads(context_path.read_text(encoding="utf-8"))
        report = render_report(bundle)

        today = datetime.now().strftime("%Y-%m-%d")
        output_path = Path(args.output) if args.output else (vault / "6-Reviews" / f"{today}-阅读分析.md")
        output_path.write_text(report, encoding="utf-8")

        print(json.dumps({"success": True, "path": str(output_path), "mode": bundle.get("runtime", {}).get("mode")}))

    except Exception as e:
        logger.exception("Report generation failed")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
