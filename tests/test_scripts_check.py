"""Test vault_check.py scripts executable check."""

from pathlib import Path
from scripts.vault_check import VaultScanner


class TestScriptsCheck:
    def test_empty_scripts_flagged(self, tmp_path: Path):
        (tmp_path / "scripts").mkdir()  # empty — no .py files

        scanner = VaultScanner(tmp_path)
        scanner.check_scripts_executable()

        assert any("python files" in x for x in scanner.errors)

    def test_scripts_with_py_files_ok(self, tmp_path: Path):
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "test.py").write_text("print('ok')")

        scanner = VaultScanner(tmp_path)
        scanner.check_scripts_executable()

        assert not any("python files" in x for x in scanner.errors)

    def test_no_scripts_dir_graceful(self, tmp_path: Path):
        """No scripts/ dir at all should not crash."""
        scanner = VaultScanner(tmp_path)
        scanner.check_scripts_executable()
        assert True
