"""Test the report rendering pipeline: Claude response → Markdown."""

from pathlib import Path
from scripts.report_generator import render_report


class TestReportPipeline:
    def test_renders_all_sections(self):
        bundle = {
            "runtime": {"mode": "V0.1"},
            "evidence": {
                "reading": {
                    "available": True,
                    "period": {"current_month_hours": 12.5, "previous_month_hours": 10.0, "change_pct": 25.0, "trend": "up", "read_days": 15},
                    "top_books": [
                        {
                            "title": "测试书",
                            "author": "作者",
                            "categories": ["心理"],
                            "total_notes": 18,
                            "notes_breakdown": {"highlights": 12, "thoughts": 4, "bookmarks": 2},
                            "reading_status": "reading",
                        }
                    ],
                    "total_books_with_notes": 41,
                    "total_notes_all_time": 1698,
                    "shelf": {"total_items": 215, "booklists": []},
                    "highlights_top3": [],
                },
                "diary": {"available": False, "entry_count": 0},
            },
        }

        report = render_report(bundle)
        assert "阅读分析" in report
        assert "阅读统计" in report
        assert "测试书" in report
        assert "本月叙事" in report  # narrative section header
