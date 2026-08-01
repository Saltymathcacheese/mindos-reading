"""End-to-end integration test: validate_report.py catches common Claude output failures."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "validate_report.py"


def _run(data: dict) -> dict:
    """Run validate_report.py with given data, return parsed JSON output."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False))
        tmp_path = f.name
    try:
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", tmp_path],
            capture_output=True, text=True,
        )
        stdout = r.stdout.strip() or "{}"
        return json.loads(stdout)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


class TestReportValidation:
    def test_valid_report_passes(self):
        data = {
            "layer1": "本月阅读12小时，笔记最多是《思考，快与慢》，阅读天数15天。上月8小时。",
            "layer2": "心理学类阅读占比从20%升至35%，可能与临床决策思维维度相关。证据：weread preferCategory。",
            "layer3": "阅读方向正在从知识获取转向理解判断过程。可信度：L1。",
            "reflection": "你最近读的内容是否影响了你的临床思维？",
            "evidence": [{"source": "WeRead", "fact": "心理学占比升"}],
        }
        result = _run(data)
        assert result["success"] is True

    def test_diagnostic_phrase_blocked(self):
        data = {
            "layer1": "本月阅读12小时，笔记最多是《思考，快与慢》，阅读天数15天。上月8小时。",
            "layer2": "心理学类阅读占比上升，可能与临床决策思维维度相关。证据：weread preferCategory。",
            "layer3": "阅读方向正在变化。L1。",
            "reflection": "你就是缺乏自律吧",
            "evidence": [],
        }
        result = _run(data)
        assert result["success"] is False
        assert any("你就是" in e for e in result["errors"])

    def test_missing_fields_blocked(self):
        data = {"layer1": "data"}
        result = _run(data)
        assert result["success"] is False
