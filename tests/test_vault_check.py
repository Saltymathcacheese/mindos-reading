"""Test vault_check.py integrity detection."""

from pathlib import Path
from scripts.vault_check import VaultScanner


class TestVaultScanner:
    def test_empty_dir_is_unhealthy(self, tmp_path: Path):
        scanner = VaultScanner(tmp_path)
        result = scanner.run()
        assert result["healthy"] is False
        assert len(result["missing"]) > 0

    def test_missing_dirs_detected(self, tmp_path: Path):
        scanner = VaultScanner(tmp_path)
        result = scanner.run()
        assert len(result["errors"]) > 0

    def test_valid_vault_is_healthy(self, tmp_path: Path):
        # Create minimal healthy structure — all REQUIRED_DIRS
        (tmp_path / "SKILL.md").write_text("# test")
        (tmp_path / "7-System").mkdir()
        (tmp_path / "7-System" / "analysis_state.yaml").write_text(
            "last_analysis:\n  date: null\n  session_id: null\n"
            "metrics:\n  reading: {}\n  diary: {}\n  learning: {}\n"
            "data_sufficiency:\n  diary_entries_total: 0\n  patterns_confirmed: 0\n"
        )
        (tmp_path / "references").mkdir()
        (tmp_path / "references" / "test.md").write_text("# ref")
        # satisfy REQUIRED_REFERENCES
        for ref in ["analysis-pipeline.md", "confidence-system.md", "interaction-rules.md"]:
            (tmp_path / "references" / ref).write_text("# required")
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "dummy.py").write_text("# ok")
        (tmp_path / "schemas").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "assets").mkdir()

        scanner = VaultScanner(tmp_path)
        result = scanner.run()
        assert result["healthy"] is True

    def test_invalid_yaml_flagged(self, tmp_path: Path):
        (tmp_path / "SKILL.md").write_text("# test")
        (tmp_path / "7-System").mkdir()
        (tmp_path / "7-System" / "analysis_state.yaml").write_text("::: bad yaml :::")
        for d in ["references", "scripts", "schemas", "tests", "assets"]:
            (tmp_path / d).mkdir()

        scanner = VaultScanner(tmp_path)
        result = scanner.run()
        assert len(result["errors"]) > 0
        assert any("Invalid YAML" in e for e in result["errors"])
