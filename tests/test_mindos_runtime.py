"""Test mindos.py runtime controller commands."""

import json
from pathlib import Path
from scripts.mindos import MindOSRuntime


class TestMindOSCommands:
    def test_check_healthy(self, tmp_path: Path):
        """Build minimal healthy vault and verify check() passes."""
        _build_healthy_vault(tmp_path)
        runtime = MindOSRuntime(tmp_path)
        result = runtime.check()
        assert result["healthy"] is True
        assert result["missing"] == []

    def test_check_unhealthy(self, tmp_path: Path):
        """Empty directory is unhealthy."""
        runtime = MindOSRuntime(tmp_path)
        result = runtime.check()
        assert result["healthy"] is False

    def test_status_returns_mode(self, tmp_path: Path):
        """Status returns V0.1 for fresh vault."""
        _build_healthy_vault(tmp_path)
        runtime = MindOSRuntime(tmp_path)
        result = runtime.status()
        assert result["success"] is True
        assert result["mode"] == "V0.1"

    def test_validate_passes(self, tmp_path: Path):
        """Validation passes for well-formed state."""
        _build_healthy_vault(tmp_path)
        runtime = MindOSRuntime(tmp_path)
        result = runtime.validate()
        assert result["success"] is True
        assert result["rule_errors"] == []


def _build_healthy_vault(root: Path) -> None:
    """Create a minimal valid MindOS vault for testing."""
    (root / "SKILL.md").write_text("# MindOS\nLoad `references/weread-collection.md`.\n", encoding="utf-8")
    for d in ["references", "scripts", "schemas", "tests", "assets"]:
        (root / d).mkdir()
    # scripts/ dir already created above
    (root / "scripts" / "dummy.py").write_text("# ok")
    # Copy the actual scripts into the temp vault for subprocess execution
    import shutil
    real_scripts = Path(__file__).resolve().parent.parent / "scripts"
    for name in ["vault_check.py", "preflight.py", "validate_state.py"]:
        src = real_scripts / name
        if src.exists():
            shutil.copy2(src, root / "scripts" / name)
    (root / "references" / "weread-collection.md").write_text("# test")
    for ref in ["analysis-pipeline.md", "confidence-system.md", "interaction-rules.md"]:
        (root / "references" / ref).write_text("# required")

    # analysis_state.yaml
    sys_dir = root / "7-System"
    sys_dir.mkdir()
    (sys_dir / "analysis_state.yaml").write_text(
        "last_analysis:\n  date: null\n  session_id: null\n"
        "metrics:\n  reading: {}\n  diary: {}\n  learning: {}\n"
        "data_sufficiency:\n  diary_entries_total: 0\n  patterns_confirmed: 0\n"
        "emotion_signals: {}\n"
        "active_themes: []\n"
        "pending_hypotheses: []\n"
        "system_self_check:\n  mode: normal\n",
        encoding="utf-8",
    )

    # analysis_state.schema.json — schemas dir already created above
    (root / "schemas" / "analysis_state.schema.json").write_text(json.dumps({
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["last_analysis", "metrics", "data_sufficiency"],
        "properties": {
            "last_analysis": {"type": "object"},
            "metrics": {"type": "object"},
            "data_sufficiency": {"type": "object"},
        }
    }))
