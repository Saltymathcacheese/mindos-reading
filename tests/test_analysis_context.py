"""Test analysis_context.py evidence extraction."""

import json
from pathlib import Path
from scripts.analysis_context import parse_frontmatter, load_diary_entries, build_context


class TestParseFrontmatter:
    def test_cleans_inline_comment(self):
        text = "---\nmood: calm # calm | anxious | tired\nenergy: 3\n---\ncontent"
        fm = parse_frontmatter(text)
        assert fm["mood"] == "calm"
        assert fm["energy"] == 3

    def test_no_frontmatter(self):
        assert parse_frontmatter("just text") == {}

    def test_empty_yaml(self):
        assert parse_frontmatter("---\n---\ncontent") == {}

    def test_preserves_clean_values(self):
        text = "---\nmood: curious\nenergy: 4\n---\ncontent"
        fm = parse_frontmatter(text)
        assert fm["mood"] == "curious"


class TestDiaryLoading:
    def test_loads_recent_entries(self, tmp_path: Path):
        exp = tmp_path / "1-Experiences"
        exp.mkdir()
        (exp / "2026-08-01-日记.md").write_text(
            "---\nmood: calm\nenergy: 3\n---\n今天写了一篇日记。\n", encoding="utf-8"
        )
        entries = load_diary_entries(exp, days=30)
        assert len(entries) == 1
        assert entries[0]["mood"] == "calm"
        assert entries[0]["energy"] == 3
        assert "写了一篇日记" in entries[0]["content_preview"]

    def test_filters_old_entries(self, tmp_path: Path):
        exp = tmp_path / "1-Experiences"
        exp.mkdir()
        (exp / "2025-01-01-日记.md").write_text(
            "---\nmood: tired\n---\n一年前的日记。\n", encoding="utf-8"
        )
        entries = load_diary_entries(exp, days=30)
        assert len(entries) == 0

    def test_handles_empty_dir(self, tmp_path: Path):
        entries = load_diary_entries(tmp_path / "nonexistent", days=30)
        assert entries == []


class TestBuildContext:
    def test_builds_minimal_bundle(self, tmp_path: Path):
        """Build context from a minimal vault with no weread data yet."""
        (tmp_path / "SKILL.md").write_text("# test")
        (tmp_path / "1-Experiences").mkdir()
        (tmp_path / "7-System").mkdir()
        (tmp_path / "7-System" / "analysis_state.yaml").write_text(
            "last_analysis:\n  date: null\n  session_id: null\n"
            "metrics:\n  reading: {}\n  diary: {}\n  learning: {}\n"
            "data_sufficiency:\n  diary_entries_total: 0\n  patterns_confirmed: 0\n"
        )

        bundle = build_context(tmp_path)
        assert bundle["runtime"]["mode"] == "V0.1"
        assert bundle["evidence"]["reading"]["available"] is False
        assert bundle["evidence"]["diary"]["entry_count"] == 0
        assert "analysis-pipeline" in bundle["available_modules"]
