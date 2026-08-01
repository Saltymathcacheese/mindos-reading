"""Regression tests — ensure Claude never produces diagnostic or personality-label output."""

import json
from pathlib import Path
from scripts.validate_response import ResponseValidator


def _make_validator(schema_path: Path) -> ResponseValidator:
    """Create validator with a minimal valid schema."""
    schema = {
        "type": "object",
        "required": ["layer1", "layer2", "layer3", "reflection", "evidence_used"],
        "properties": {
            "layer1": {"type": "object", "required": ["content", "confidence"], "properties": {"content": {"type": "string"}, "confidence": {"type": "string"}}},
            "layer2": {"type": "object", "required": ["content", "confidence"], "properties": {"content": {"type": "string"}, "confidence": {"type": "string"}}},
            "layer3": {"type": "object", "required": ["content", "confidence"], "properties": {"content": {"type": "string"}, "confidence": {"type": "string"}}},
            "reflection": {"type": "string"},
            "evidence_used": {"type": "array"},
        },
    }
    schema_file = schema_path / "schema.json"
    schema_file.write_text(json.dumps(schema))
    return ResponseValidator(schema_file)


DIAGNOSTIC_SAMPLES = [
    "你就是缺乏自律",
    "你有逃避心理",
    "你的问题是过度完美主义",
    "你是一个焦虑型人格",
]

PERSONALITY_SAMPLES = [
    "这表明你可能有完美主义倾向",
    "你的回避型行为模式",
    "这是典型的焦虑型人格表现",
    "你有强迫症的表现",
]

SAFE_SAMPLES = [
    "本月观察到阅读偏好从工具书转向心理学类书籍。这个变化可能与学期阶段有关。（L1）",
    "最近30天出现'压力期非教材阅读增加'的行为模式，证据来自3条日记和阅读时段数据。可信度：L2。",
    "你的阅读方向正在从效率优化转向自我理解。这不是好坏判断，只是一个可观察的迁移。（L1）",
]


class TestRegression:
    def test_diagnostic_phrases_blocked(self, tmp_path: Path):
        v = _make_validator(tmp_path)
        for text in DIAGNOSTIC_SAMPLES:
            data = {
                "layer1": {"content": text, "confidence": "L1"},
                "layer2": {"content": "ok", "confidence": "L1"},
                "layer3": {"content": "ok", "confidence": "L1"},
                "reflection": "今天感觉如何？",
                "evidence_used": [{"source": "x", "fact": "y"}],
            }
            errors = v.validate(data)
            assert len(errors) > 0, f"DIAGNOSTIC NOT BLOCKED: '{text}'"

    def test_personality_labels_blocked(self, tmp_path: Path):
        v = _make_validator(tmp_path)
        for text in PERSONALITY_SAMPLES:
            data = {
                "layer1": {"content": text, "confidence": "L1"},
                "layer2": {"content": "ok", "confidence": "L1"},
                "layer3": {"content": "ok", "confidence": "L1"},
                "reflection": "是否影响了你的思维？",
                "evidence_used": [{"source": "x", "fact": "y"}],
            }
            errors = v.validate(data)
            assert len(errors) > 0, f"PERSONALITY LABEL NOT BLOCKED: '{text}'"

    def test_safe_outputs_clear(self, tmp_path: Path):
        v = _make_validator(tmp_path)
        for text in SAFE_SAMPLES:
            data = {
                "layer1": {"content": text, "confidence": "L1"},
                "layer2": {"content": text, "confidence": "L1"},
                "layer3": {"content": text, "confidence": "L1"},
                "reflection": "是否影响了你的思维？",
                "evidence_used": [{"source": "x", "fact": "y"}],
            }
            errors = v.validate(data)
            assert errors == [], f"SAFE OUTPUT FALSE-POSITIVE: '{text}' → {errors}"
