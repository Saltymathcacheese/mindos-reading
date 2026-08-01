"""Test state_update.py update logic and backup behavior."""

import pytest
from pathlib import Path
from scripts.state_update import update_state, validate_state, StateValidationError


class TestUpdateLogic:
    def test_updates_last_analysis(self):
        state = {
            "last_analysis": {},
            "metrics": {"reading": {}, "diary": {}, "learning": {}},
            "data_sufficiency": {},
        }
        result = update_state(state, diary_count=5)
        assert result["last_analysis"]["date"] is not None
        assert result["last_analysis"]["session_id"] is not None

    def test_updates_reading_metrics(self):
        state = {
            "last_analysis": {},
            "metrics": {"reading": {}, "diary": {}, "learning": {}},
            "data_sufficiency": {},
        }
        result = update_state(state, total_hours=12.5, books_active=3, notes_total=1698)
        reading = result["metrics"]["reading"]
        assert reading["total_hours_30d"]["value"] == 12.5
        assert reading["books_active"]["value"] == 3
        assert reading["notes_total"]["value"] == 1698

    def test_updates_diary_count(self):
        state = {
            "last_analysis": {},
            "metrics": {"reading": {}, "diary": {}, "learning": {}},
            "data_sufficiency": {},
        }
        result = update_state(state, diary_count=10)
        assert result["data_sufficiency"]["diary_entries_total"] == 10

    def test_increments_session_count(self):
        state = {
            "last_analysis": {},
            "metrics": {"session_count": 5, "reading": {}, "diary": {}, "learning": {}},
            "data_sufficiency": {},
        }
        result = update_state(state)
        assert result["metrics"]["session_count"] == 6

    def test_initial_session_count(self):
        state = {
            "last_analysis": {},
            "metrics": {"reading": {}, "diary": {}, "learning": {}},
            "data_sufficiency": {},
        }
        result = update_state(state)
        assert result["metrics"]["session_count"] == 1

    def test_preserves_existing_fields(self):
        state = {
            "last_analysis": {},
            "metrics": {"reading": {"fiction_ratio": {"value": 0.2}}, "diary": {}, "learning": {}},
            "data_sufficiency": {"patterns_confirmed": 2, "actions_attempted": 1},
        }
        result = update_state(state, total_hours=10.0)
        assert result["metrics"]["reading"]["fiction_ratio"]["value"] == 0.2
        assert result["data_sufficiency"]["patterns_confirmed"] == 2
        assert result["data_sufficiency"]["actions_attempted"] == 1


class TestValidation:
    def test_valid_minimal_state(self):
        state = {
            "last_analysis": {},
            "metrics": {"reading": {}, "diary": {}, "learning": {}},
            "data_sufficiency": {},
        }
        validate_state(state)  # should not raise

    def test_missing_section_raises(self):
        state = {"last_analysis": {}}
        with pytest.raises(StateValidationError):
            validate_state(state)
