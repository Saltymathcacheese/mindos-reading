#!/usr/bin/env python3
"""
MindOS reflection_generator.py — Daily reflection prompt scaffold.

Reads analysis_context.json and generates a structured prompt file.
The actual reflection question is left as a placeholder for Claude to fill
using references/analysis-pipeline.md Layer 3.

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("mindos.reflection")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def render_prompt(bundle: dict) -> str:
    """Generate a reflection prompt file with Claude fill placeholder."""
    today = datetime.now().strftime("%Y-%m-%d")
    reading = bundle.get("evidence", {}).get("reading", {})
    diary = bundle.get("evidence", {}).get("diary", {})

    # Context hints for Claude
    context_lines = []
    if reading.get("available"):
        period = reading["period"]
        top = reading.get("top_books", [])
        book_names = [b["title"] for b in top[:3]]
        context_lines.append(f"本月阅读 {period['current_month_hours']:.1f} 小时，笔记最多的书：{'、'.join(book_names)}")
    if diary.get("available"):
        context_lines.append(f"本月 {diary['entry_count']} 篇日记")

    context_str = "；".join(context_lines) if context_lines else "（无上下文数据）"

    return (
        f"---\n"
        f"date: {today}\n"
        f"type: daily-prompt\n"
        f"source: reading-analysis\n"
        f"---\n\n"
        f"# 今天的反思\n\n"
        f"<!-- Claude: 根据上述上下文生成一个问题（≤50字）。\n"
        f"见 references/analysis-pipeline.md Layer 3 的反思问题生成规则。\n"
        f"问题应连接阅读模式与用户的实际生活，开放且不带评判。 -->\n\n"
        f"**上下文：** {context_str}\n\n"
        f"**反思问题：** <!-- Claude fill -->\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Generate MindOS reflection prompt scaffold")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--output", default=None, help="Output path (default: 0-Inbox/YYYY-MM-DD-反思引导.md)")
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
        prompt = render_prompt(bundle)

        today = datetime.now().strftime("%Y-%m-%d")
        output_path = Path(args.output) if args.output else (vault / "0-Inbox" / f"{today}-反思引导.md")
        output_path.write_text(prompt, encoding="utf-8")

        print(json.dumps({"success": True, "path": str(output_path)}))

    except Exception as e:
        logger.exception("Prompt generation failed")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
