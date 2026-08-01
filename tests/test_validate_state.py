"""Test validate_state.py dual-layer validation."""

import json
import pytest
from pathlib import Path
from scripts.validate_state import StateValidator


SCHEMA_CONTENT = json.dumps({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["last_analysis", "metrics", "data_sufficiency"],
    "properties": {
        "data_sufficiency": {
            "type": "object",
            "properties": {
                "diary_entries_total": {"type": "integer"},
                "patterns_confirmed": {"type": "integer"},
            }
        },
        "last_analysis": {
            "type": "object",
            "properties": {
                "mode": {"type": "string"}
            }
        },
        "system_self_check": {
            "type": "object",
            "properties": {
                "mode": {"type": "string"}
            }
        },
        "metrics": {
            "type": "object",
            "properties": {
                "session_count": {"type": "integer"}
            }
        }
    }
})


def _make_validator(schema_json: str = SCHEMA_CONTENT) -> StateValidator:
    """Create a StateValidator with an in-memory schema."""
    v = StateValidator(schema_path=None)
    v.schema = json.loads(schema_json)
    return v


class TestSchemaValidation:
    def test_valid_state_passes(self):
        v = _make_validator()
        data = {
            "last_analysis": {"date": "2026-08-01"},
            "metrics": {},
            "data_sufficiency": {"diary_entries_total": 1},
        }
        errors = v.validate_schema(data)
        assert errors == []

    def test_missing_required_section_fails(self):
        v = _make_validator()
        data = {"last_analysis": {}}
        errors = v.validate_schema(data)
        assert len(errors) > 0


class TestRuleValidation:
    def test_negative_diary(self):
        v = _make_validator()
        data = {
            "data_sufficiency": {"diary_entries_total": -1},
        }
        errors = v.validate_rules(data)
        assert any("negative" in e for e in errors)

    def test_negative_patterns(self):
        v = _make_validator()
        data = {
            "data_sufficiency": {"patterns_confirmed": -5},
        }
        errors = v.validate_rules(data)
        assert any("patterns_confirmed" in e for e in errors)

    def test_session_without_date(self):
        v = _make_validator()
        data = {
            "last_analysis": {},
            "metrics": {"session_count": 5},
            "data_sufficiency": {},
        }
        errors = v.validate_rules(data)
        assert any("last_analysis.date" in e for e in errors)

    def test_invalid_mode(self):
        v = _make_validator()
        data = {
            "last_analysis": {"mode": "V5.0"},
            "data_sufficiency": {},
        }
        errors = v.validate_rules(data)
        assert any("Invalid mode" in e for e in errors)

    def test_invalid_safe_mode(self):
        v = _make_validator()
        data = {
            "system_self_check": {"mode": "panic"},
            "data_sufficiency": {},
        }
        errors = v.validate_rules(data)
        assert any("system_self_check" in e for e in errors)

    def test_valid_data_no_errors(self):
        v = _make_validator()
        data = {
            "last_analysis": {"date": "2026-08-01", "mode": "V0.1"},
            "metrics": {"session_count": 1},
            "data_sufficiency": {"diary_entries_total": 5, "patterns_confirmed": 0},
            "system_self_check": {"mode": "normal"},
        }
        errors = v.validate_rules(data)
        assert errors == []

    def test_full_validate_pass(self):
        v = _make_validator()
        data = {
            "last_analysis": {"date": "2026-08-01"},
            "metrics": {},
            "data_sufficiency": {"diary_entries_total": 1, "patterns_confirmed": 0},
        }
        result = v.validate(data)
        assert result["success"] is True


class TestSchemaNotAvailable:
    def test_skips_when_no_jsonschema(self, monkeypatch):
        """Graceful degradation when jsonschema is not installed."""
        monkeypatch.setattr("scripts.validate_state.HAS_JSONSCHEMA", False)
        v = _make_validator()
        data = {}
        errors = v.validate_schema(data)
        assert errors == []  # skipped, not failed
