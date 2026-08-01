"""Test preflight.py version gating and state extraction."""

import pytest
from scripts.preflight import StateReader


class TestVersionGate:
    def test_v0_1_when_no_data(self):
        assert StateReader._detect_mode(0, 0) == "V0.1"

    def test_v0_1_when_few_diaries(self):
        assert StateReader._detect_mode(5, 0) == "V0.1"
        assert StateReader._detect_mode(9, 2) == "V0.1"

    def test_v0_2_when_enough_diaries_no_patterns(self):
        assert StateReader._detect_mode(10, 0) == "V0.2"
        assert StateReader._detect_mode(50, 2) == "V0.2"

    def test_v0_3_when_patterns_confirmed(self):
        assert StateReader._detect_mode(10, 3) == "V0.3"
        assert StateReader._detect_mode(100, 5) == "V0.3"


class TestStateExtraction:
    def test_extracts_diary_count(self):
        reader = StateReader()
        state = {"data_sufficiency": {"diary_entries_total": 7, "patterns_confirmed": 0}}
        ctx = reader.extract_context(state)
        assert ctx.diary_count == 7
        assert ctx.patterns_confirmed == 0

    def test_extracts_last_analysis_date(self):
        reader = StateReader()
        state = {
            "data_sufficiency": {"diary_entries_total": 0, "patterns_confirmed": 0},
            "last_analysis": {"date": "2026-08-01"},
        }
        ctx = reader.extract_context(state)
        assert ctx.last_analysis == "2026-08-01"

    def test_respects_explicit_mode_override(self):
        reader = StateReader()
        state = {
            "data_sufficiency": {"diary_entries_total": 100, "patterns_confirmed": 10},
            "last_analysis": {"mode": "V0.1"},
        }
        ctx = reader.extract_context(state)
        assert ctx.mode == "V0.1"  # explicit override wins

    def test_detects_safe_mode(self):
        reader = StateReader()
        state = {
            "data_sufficiency": {"diary_entries_total": 0, "patterns_confirmed": 0},
            "system_self_check": {"mode": "safe"},
        }
        ctx = reader.extract_context(state)
        assert ctx.safe_mode is True
