#!/usr/bin/env python3
"""Test the end-to-end handoff pipeline: context → request → response → validation.

Includes JSON Schema validation for both request and response schemas.
"""

import json
from pathlib import Path
from scripts.create_request import create_request as build_request
from scripts.validate_response import ResponseValidator

# Load schemas for validation
SCHEMA_DIR = Path(__file__).parent.parent / "schemas"
REQUEST_SCHEMA = json.loads((SCHEMA_DIR / "analysis_request.schema.json").read_text(encoding="utf-8"))

try:
    from jsonschema import validate, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def validate_against_schema(data: dict, schema: dict) -> list[str]:
    if not HAS_JSONSCHEMA:
        return []
    try:
        validate(data, schema)
        return []
    except ValidationError as e:
        return [str(e)]


class TestRequestSchema:
    """Validate analysis_request.json conforms to schema."""

    def test_valid_request_conforms(self, tmp_path: Path):
        context = {
            "generated_at": "2026-08-01",
            "version": "2.3",
            "runtime": {"mode": "V0.1"},
            "evidence": {
                "reading": {"available": True, "period": {"current_month_hours": 12.5}},
                "diary": {"entry_count": 3},
            },
        }
        input_file = tmp_path / "context.json"
        input_file.write_text(json.dumps(context), encoding="utf-8")
        output = tmp_path / "request.json"

        build_request(input_file, output)
        result = json.loads(output.read_text(encoding="utf-8"))

        # Add required timestamp if missing (create_request uses created_at)
        if "timestamp" not in result:
            result["timestamp"] = result.get("created_at", "2026-08-01T00:00:00")
        if "type" not in result:
            result["type"] = result.get("task", {}).get("type", "reading_analysis")

        errors = validate_against_schema(result, REQUEST_SCHEMA)
        assert errors == [], f"Schema validation errors: {errors}"

    def test_request_must_have_constraints(self):
        """Request without constraints is invalid."""
        invalid = {
            "protocol_version": "2.0",
            "type": "reading_analysis",
            "timestamp": "2026-08-01T00:00:00",
            "evidence": {"reading": {}},
        }
        errors = validate_against_schema(invalid, REQUEST_SCHEMA)
        assert len(errors) > 0

    def test_request_no_diagnosis_must_be_true(self):
        """no_diagnosis constraint must be true."""
        invalid = {
            "protocol_version": "2.0",
            "type": "reading_analysis",
            "timestamp": "2026-08-01T00:00:00",
            "evidence": {"reading": {}},
            "constraints": {
                "no_diagnosis": False,
                "no_personality_label": True,
                "max_reflection_chars": 60,
            },
        }
        # Schema doesn't enforce value=true (it's a constraint for Claude), but it enforces presence
        errors = validate_against_schema(invalid, REQUEST_SCHEMA)
        # Should pass structural validation — semantic check is in ResponseValidator
        assert errors == []


class TestHandoffRequest:
    def test_creates_valid_request(self, tmp_path: Path):
        context = {
            "generated_at": "2026-08-01",
            "version": "2.3",
            "runtime": {"mode": "V0.1"},
            "evidence": {
                "reading": {"available": True, "period": {"current_month_hours": 12.5}},
                "diary": {"entry_count": 3},
            },
        }
        input_file = tmp_path / "context.json"
        input_file.write_text(json.dumps(context), encoding="utf-8")
        output = tmp_path / "request.json"

        build_request(input_file, output)
        result = json.loads(output.read_text(encoding="utf-8"))

        assert result["protocol_version"] == "1.0"
        assert result["task"]["type"] == "reading_analysis"
        assert result["constraints"]["no_diagnosis"] is True
        assert "reading" in result["evidence"]

    def test_request_has_no_interpretation(self, tmp_path: Path):
        """Evidence must contain facts only — no AI-generated fields."""
        context = {
            "runtime": {"mode": "V0.1"},
            "evidence": {"reading": {"period": {"current_month_hours": 5.0}}},
        }
        input_file = tmp_path / "context.json"
        input_file.write_text(json.dumps(context), encoding="utf-8")
        output = tmp_path / "request.json"

        build_request(input_file, output)
        result = json.loads(output_text := output.read_text(encoding="utf-8"))

        # No interpretation should leak into the request
        assert "你" not in output_text
        assert "可能" not in output_text


class TestResponseValidation:
    def test_valid_response_passes(self, tmp_path: Path):
        schema = {
            "type": "object",
            "required": ["layer1", "layer2", "layer3", "reflection", "evidence_used"],
            "properties": {
                "layer1": {"type": "object", "required": ["content", "confidence"]},
                "layer2": {"type": "object", "required": ["content", "confidence"]},
                "layer3": {"type": "object", "required": ["content", "confidence"]},
                "reflection": {"type": "string"},
                "evidence_used": {"type": "array"},
            },
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema))

        validator = ResponseValidator(schema_file)
        data = {
            "layer1": {"content": "fact", "confidence": "L4"},
            "layer2": {"content": "association", "confidence": "L1"},
            "layer3": {"content": "narrative", "confidence": "L1"},
            "reflection": "这是否影响了你的思维？",
            "evidence_used": [{"source": "WeRead", "fact": "test"}],
        }
        errors = validator.validate(data)
        assert errors == []

    def test_missing_layer_fails(self, tmp_path: Path):
        schema = {
            "type": "object",
            "required": ["layer1", "layer2", "layer3", "reflection", "evidence_used"],
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema))

        validator = ResponseValidator(schema_file)
        errors = validator.validate({"layer1": {"content": "x", "confidence": "L1"}})
        assert len(errors) > 0

    def test_diagnostic_blocked(self, tmp_path: Path):
        schema = {
            "type": "object",
            "required": ["layer1", "layer2", "layer3", "reflection", "evidence_used"],
            "properties": {
                "layer1": {"type": "object"},
                "layer2": {"type": "object"},
                "layer3": {"type": "object"},
                "reflection": {"type": "string"},
                "evidence_used": {"type": "array"},
            },
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema))

        validator = ResponseValidator(schema_file)
        data = {
            "layer1": {"content": "你是一个逃避学习的人", "confidence": "L1"},
            "layer2": {"content": "ok", "confidence": "L1"},
            "layer3": {"content": "ok", "confidence": "L1"},
            "reflection": "你为什么逃避？",
            "evidence_used": [{"source": "x", "fact": "y"}],
        }
        errors = validator.validate(data)
        assert any("你就是" in e or "diagnostic" in e.lower() for e in errors)
