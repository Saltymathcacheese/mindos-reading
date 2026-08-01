"""Test vault_check.py reference coverage."""

from pathlib import Path
from scripts.vault_check import VaultScanner, REQUIRED_REFERENCES


class TestReferenceCoverage:
    def test_missing_reference_flagged(self, tmp_path: Path):
        scanner = VaultScanner(tmp_path)
        scanner.check_reference_coverage()

        # All REQUIRED_REFERENCES are missing → should warn
        assert len(scanner.warnings) >= len(REQUIRED_REFERENCES)

    def test_all_present_no_warnings(self, tmp_path: Path):
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        for item in REQUIRED_REFERENCES:
            (ref_dir / item).write_text("# test")

        scanner = VaultScanner(tmp_path)
        scanner.check_reference_coverage()
        assert len(scanner.warnings) == 0
