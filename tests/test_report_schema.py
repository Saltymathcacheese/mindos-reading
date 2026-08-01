"""Test report.schema.json validation constraints."""

import json
import pytest
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "report.schema.json"


@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


class TestReportSchema:
    def test_valid_report_passes(self, schema):
        """A complete report with all sections should validate."""
        from jsonschema import validate
        report = {
            "layer1": "本月阅读 12.5 小时，笔记最多的书是《思考，快与慢》（18条）。阅读天数 15 天。",
            "layer2": "心理学类阅读占比从 20% 升至 35%，可能与临床决策思维维度相关。证据：weread preferCategory 数据。",
            "layer3": "阅读焦点正在从效率优化转向不确定性管理。当前可信度：L1（初步信号）。",
            "reflection": "你最近读的内容，是否开始影响你理解临床问题的方式？",
        }
        validate(report, schema)  # should not raise

    def test_missing_layer_fails(self, schema):
        from jsonschema import validate, ValidationError
        report = {
            "layer1": "stats...",
        }
        with pytest.raises(ValidationError):
            validate(report, schema)

    def test_reflection_too_long_fails(self, schema):
        from jsonschema import validate, ValidationError
        report = {
            "layer1": "a" * 60,
            "layer2": "b" * 25,
            "layer3": "c" * 40,
            "reflection": "x" * 70,  # exceeds 60
        }
        with pytest.raises(ValidationError):
            validate(report, schema)

    def test_short_layer1_fails(self, schema):
        from jsonschema import validate, ValidationError
        report = {
            "layer1": "short",  # < 40 chars
            "layer2": "b" * 25,
            "layer3": "c" * 40,
            "reflection": "ok",
        }
        with pytest.raises(ValidationError):
            validate(report, schema)
