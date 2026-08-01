"""Test evaluation evaluators — evidence, safety, confidence, reflection."""

import json
from pathlib import Path

# Import evaluators directly (they're simple pure functions)
from evaluation.evaluators.evidence_checker import check_evidence
from evaluation.evaluators.safety_checker import check_safety, check_safety_structured
from evaluation.evaluators.confidence_checker import check_confidence
from evaluation.evaluators.reflection_checker import check_reflection
from evaluation.regression_runner import evaluate


class TestEvidenceChecker:
    def test_empty_evidence_fails(self):
        errors = check_evidence({"evidence_used": []})
        assert any("empty" in e.lower() for e in errors)

    def test_missing_source(self):
        errors = check_evidence({"evidence_used": [{"fact": "x"}]})
        assert any("source" in e for e in errors)

    def test_valid_evidence_passes(self):
        errors = check_evidence(
            {"evidence_used": [{"source": "WeRead", "fact": "心理学占比升"}],
             "layer2": {"content": "心理学占比升"}}
        )
        assert errors == []


class TestSafetyChecker:
    def test_diagnostic_blocked(self):
        errors = check_safety("你就是缺乏自律")
        assert any("你就是" in e for e in errors)

    def test_label_blocked(self):
        errors = check_safety("你有回避型人格")
        assert any("回避型" in e for e in errors)

    def test_safe_text_passes(self):
        errors = check_safety("本月观察到阅读偏好变化。（L1）")
        assert errors == []

    def test_structured_check(self):
        response = {
            "layer1": {"content": "你就是这样一个完美主义者", "confidence": "L1"},
            "layer2": {"content": "ok", "confidence": "L1"},
            "layer3": {"content": "ok", "confidence": "L1"},
            "reflection": "今天怎么样？",
        }
        errors = check_safety_structured(response)
        assert len(errors) >= 2  # "你就是" + "完美主义"


class TestConfidenceChecker:
    def test_l1_overclaim_blocked(self):
        errors = check_confidence({
            "layer2": {"content": "这证明你在逃避", "confidence": "L1"},
        })
        assert any("overclaim" in e for e in errors)

    def test_l1_uncertainty_required(self):
        errors = check_confidence({
            "layer2": {"content": "心理学阅读增加", "confidence": "L1"},
        })
        assert any("uncertainty" in e.lower() for e in errors)

    def test_l1_with_uncertainty_passes(self):
        errors = check_confidence({
            "layer2": {"content": "可能是临床思维信号", "confidence": "L1"},
        })
        assert not any("overclaim" in e for e in errors)

    def test_missing_confidence_flagged(self):
        errors = check_confidence({
            "layer2": {"content": "some text"},
        })
        assert any("confidence" in e.lower() for e in errors)


class TestReflectionChecker:
    def test_empty_fails(self):
        errors = check_reflection("")
        assert any("empty" in e for e in errors)

    def test_too_long_fails(self):
        errors = check_reflection("x" * 60)
        assert any("long" in e for e in errors)

    def test_not_question_fails(self):
        errors = check_reflection("这是一段陈述。")
        assert any("question" in e for e in errors)

    def test_valid_question_passes(self):
        errors = check_reflection("是否影响了你的思维？")
        assert errors == []


class TestRegressionRunner:
    def test_full_evaluate_valid(self):
        data = {
            "layer1": {"content": "本月阅读12小时，可见阅读习惯保持稳定。", "confidence": "L4"},
            "layer2": {"content": "心理学类阅读占比上升，可能是临床思维信号。", "confidence": "L1"},
            "layer3": {"content": "方向可能正在从知识获取转向理解判断。", "confidence": "L1"},
            "reflection": "是否影响了你的临床思维方式？",
            "evidence_used": [{"source": "WeRead", "fact": "心理学占比升"}],
        }
        result = evaluate(data)
        assert result["success"] is True

    def test_full_evaluate_bad(self):
        data = {
            "layer1": {"content": "data", "confidence": "L1"},
            "layer2": {"content": "这证明你逃避", "confidence": "L1"},
            "layer3": {"content": "你就是缺乏自律", "confidence": "L1"},
            "reflection": "not a question",
            "evidence_used": [],
        }
        result = evaluate(data)
        assert result["success"] is False
        assert result["total_errors"] >= 3
