"""Test memory subsystem — scorer, collector, validator."""

import json
from pathlib import Path
from scripts.memory_scorer import calculate_score, score_batch, filter_top
from scripts.memory_validator import validate_memory, validate_batch
from scripts.memory_collector import MemoryCollector


class TestMemoryScorer:
    def test_basic_score(self):
        item = {"impact": 8, "repetition": 5, "future_relevance": 10, "emotional_weight": 3}
        score = calculate_score(item)
        assert 5 < score < 10

    def test_low_emotion_weight(self):
        """Emotion should contribute less than future relevance."""
        high_emo = {"impact": 5, "repetition": 5, "future_relevance": 5, "emotional_weight": 10}
        high_future = {"impact": 5, "repetition": 5, "future_relevance": 10, "emotional_weight": 5}
        assert calculate_score(high_future) > calculate_score(high_emo)

    def test_score_batch_sorts_desc(self):
        candidates = [
            {"impact": 3, "repetition": 1, "future_relevance": 3, "emotional_weight": 1},
            {"impact": 8, "repetition": 5, "future_relevance": 9, "emotional_weight": 2},
        ]
        scored = score_batch(candidates)
        assert scored[0]["score"] >= scored[1]["score"]

    def test_filter_top(self):
        scored = [
            {"id": "a", "score": 9.0},
            {"id": "b", "score": 7.0},
            {"id": "c", "score": 3.0},
        ]
        top = filter_top(scored, top_n=2)
        assert len(top) == 2
        assert top[0]["id"] == "a"


class TestMemoryValidator:
    def test_valid_entry_passes(self):
        entry = {
            "id": "mem_001",
            "content": "过去90天观察到复习效率在晚间降低。",
            "source": ["6-Reviews/2026-08-01-阅读分析.md"],
            "score": 7.5,
            "status": "candidate",
        }
        errors = validate_memory(entry)
        assert errors == []

    def test_diagnostic_blocked(self):
        entry = {
            "id": "mem_001",
            "content": "你是一个完美主义者",
            "source": ["x"],
            "score": 5,
            "status": "candidate",
        }
        errors = validate_memory(entry)
        assert len(errors) > 0

    def test_missing_source_fails(self):
        entry = {
            "id": "mem_001",
            "content": "valid content",
            "source": [],
            "score": 5,
            "status": "candidate",
        }
        errors = validate_memory(entry)
        assert any("source" in e.lower() for e in errors)

    def test_invalid_score_fails(self):
        entry = {
            "id": "mem_001",
            "content": "valid",
            "source": ["x"],
            "score": 15,
            "status": "active",
        }
        errors = validate_memory(entry)
        assert any("score" in e.lower() for e in errors)

    def test_invalid_status_fails(self):
        entry = {
            "id": "mem_001",
            "content": "valid",
            "source": ["x"],
            "score": 5,
            "status": "deleted",
        }
        errors = validate_memory(entry)
        assert any("status" in e.lower() for e in errors)


class TestMemoryCollector:
    def test_collects_from_multiple_folders(self, tmp_path: Path):
        for folder in ("6-Reviews", "1-Experiences", "3-Patterns"):
            (tmp_path / folder).mkdir(parents=True)
        (tmp_path / "1-Experiences" / "2026-08-01-日记.md").write_text("# test diary", encoding="utf-8")
        (tmp_path / "6-Reviews" / "2026-08-01-阅读分析.md").write_text("# test review", encoding="utf-8")

        collector = MemoryCollector(tmp_path)
        result = collector.collect()
        assert len(result["diary"]) >= 1
        assert len(result["reviews"]) >= 1
