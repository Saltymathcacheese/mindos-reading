"""Test vault_check.py dispatch link integrity."""

from pathlib import Path
from scripts.vault_check import VaultScanner


class TestDispatchLinks:
    def test_broken_reference_flagged(self, tmp_path: Path):
        # Create SKILL.md referencing a file that does not exist
        (tmp_path / "SKILL.md").write_text(
            "Load `references/not_exist.md` for details.",
            encoding="utf-8",
        )
        (tmp_path / "references").mkdir()
        # Do NOT create not_exist.md

        scanner = VaultScanner(tmp_path)
        scanner.check_dispatch_links()

        assert any("Broken dispatch reference" in x for x in scanner.errors)

    def test_valid_reference_no_errors(self, tmp_path: Path):
        (tmp_path / "SKILL.md").write_text(
            "Load `references/weread-collection.md` for details.",
            encoding="utf-8",
        )
        (tmp_path / "references").mkdir()
        (tmp_path / "references" / "weread-collection.md").write_text("# test")

        scanner = VaultScanner(tmp_path)
        scanner.check_dispatch_links()

        assert len(scanner.errors) == 0

    def test_no_skill_md_graceful(self, tmp_path: Path):
        """No SKILL.md at all should not crash."""
        scanner = VaultScanner(tmp_path)
        scanner.check_dispatch_links()
        # Should not raise, just skip
        assert True
