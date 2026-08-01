"""Test weread_fetch.py normalizer and sampler against real API response shapes."""

import pytest
from scripts.weread_fetch import WeReadNormalizer, HighlightSampler


class TestNormalizeBooks:
    def test_parses_real_notebook_shape(self):
        """Verify we handle the actual nested book.bookId / book.title structure."""
        notebooks = [
            {
                "bookId": "39128586",
                "book": {
                    "bookId": "39128586",
                    "title": "你是你吃出来的",
                    "author": "夏萌",
                    "categories": [{"title": "医学健康"}],
                    "deepLink": "https://weread.qq.com/...",
                },
                "reviewCount": 5,
                "noteCount": 206,
                "bookmarkCount": 31,
                "markedStatus": 4,
                "readingProgress": 87,
            }
        ]
        result = WeReadNormalizer.normalize_books(notebooks)
        assert len(result) == 1
        assert result[0]["title"] == "你是你吃出来的"
        assert result[0]["book_id"] == "39128586"
        assert result[0]["total_notes"] == 242
        assert result[0]["categories"] == ["医学健康"]
        assert result[0]["note_count"] == 206

    def test_sorts_by_total_notes_desc(self):
        notebooks = [
            {"bookId": "1", "book": {"title": "A"}, "reviewCount": 0, "noteCount": 5, "bookmarkCount": 0},
            {"bookId": "2", "book": {"title": "B"}, "reviewCount": 0, "noteCount": 50, "bookmarkCount": 0},
            {"bookId": "3", "book": {"title": "C"}, "reviewCount": 0, "noteCount": 10, "bookmarkCount": 0},
        ]
        result = WeReadNormalizer.normalize_books(notebooks)
        assert result[0]["title"] == "B"
        assert result[1]["title"] == "C"
        assert result[2]["title"] == "A"

    def test_handles_empty_list(self):
        assert WeReadNormalizer.normalize_books([]) == []


class TestNormalizeStats:
    def test_seconds_conversion(self):
        result = WeReadNormalizer.seconds_to_display(3661)
        assert result["hours"] == 1
        assert result["minutes"] == 1
        assert result["total_seconds"] == 3661

    def test_zero_seconds(self):
        result = WeReadNormalizer.seconds_to_display(0)
        assert result["hours"] == 0
        assert result["minutes"] == 0

    def test_normalize_stats_passes_through(self):
        data = {"totalReadTime": 7200, "readDays": 15, "dayAverageReadTime": 480, "compare": 0.2}
        result = WeReadNormalizer.normalize_stats(data)
        assert result["reading_time"]["hours"] == 2
        assert result["read_days"] == 15
        assert result["compare"] == 0.2


class TestHighlightSampler:
    def test_samples_evenly(self):
        highlights = [{"markText": f"text {i}"} for i in range(20)]
        result = HighlightSampler.sample(highlights, limit=5)
        assert len(result) == 5
        assert all("text" in r["text"] for r in result)

    def test_returns_all_when_under_limit(self):
        highlights = [{"markText": f"text {i}"} for i in range(3)]
        result = HighlightSampler.sample(highlights, limit=8)
        assert len(result) == 3

    def test_empty_list(self):
        assert HighlightSampler.sample([], limit=8) == []
