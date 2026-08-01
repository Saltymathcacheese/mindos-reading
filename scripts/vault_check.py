#!/usr/bin/env python3
"""
MindOS vault_check.py — Environment integrity checker.

Checks:
- Required files (SKILL.md, analysis_state.yaml)
- Required directories (references, scripts, 7-System, schemas, tests, assets)
- YAML validity (analysis_state.yaml)
- Reference markdown presence + critical coverage
- Scripts directory executable content
- SKILL.md dispatch link integrity

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path

from ruamel.yaml import YAML

# =========================
# Logging
# =========================
logger = logging.getLogger("mindos.vault_check")


def setup_logging(verbose: bool = False):
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# =========================
# Constants
# =========================
REQUIRED_FILES = [
    "SKILL.md",
    "7-System/analysis_state.yaml",
]

REQUIRED_DIRS = [
    "references",
    "scripts",
    "7-System",
    "schemas",
    "tests",
    "assets",
]

REQUIRED_REFERENCES = [
    "analysis-pipeline.md",
    "confidence-system.md",
    "interaction-rules.md",
]

YAML_FILES = [
    "7-System/analysis_state.yaml",
]


# =========================
# Scanner
# =========================
class VaultScanner:
    def __init__(self, root: Path):
        self.root = root
        self.missing: list[str] = []
        self.warnings: list[str] = []
        self.errors: list[str] = []

    # ── Basic checks ──

    def check_files(self):
        for file in REQUIRED_FILES:
            path = self.root / file
            if not path.exists():
                self.missing.append(file)

    def check_directories(self):
        for directory in REQUIRED_DIRS:
            path = self.root / directory
            if not path.exists():
                self.errors.append(f"Missing directory: {directory}")

    def check_yaml(self):
        yaml = YAML()
        for file in YAML_FILES:
            path = self.root / file
            if not path.exists():
                continue
            try:
                with path.open("r", encoding="utf-8") as f:
                    yaml.load(f)
            except Exception as e:
                self.errors.append(f"Invalid YAML {file}: {e}")

    def check_references(self):
        """Basic check: references/ exists and has .md files."""
        reference_dir = self.root / "references"
        if not reference_dir.exists():
            return
        md_files = list(reference_dir.glob("*.md"))
        if len(md_files) == 0:
            self.warnings.append("references directory empty")

    # ── Enhanced checks (v2.1) ──

    def check_reference_coverage(self):
        """Verify critical reference files exist."""
        ref_dir = self.root / "references"
        for item in REQUIRED_REFERENCES:
            if not (ref_dir / item).exists():
                self.warnings.append(f"Missing critical reference: {item}")

    def check_scripts_executable(self):
        """Verify scripts/ directory contains python files (not empty)."""
        scripts_dir = self.root / "scripts"
        if not scripts_dir.exists():
            return
        py_files = list(scripts_dir.glob("*.py"))
        if len(py_files) == 0:
            self.errors.append("scripts directory has no python files")

    def check_dispatch_links(self):
        """Parse SKILL.md for references/*.md mentions and verify they exist."""
        skill_path = self.root / "SKILL.md"
        if not skill_path.exists():
            return
        text = skill_path.read_text(encoding="utf-8")
        refs = re.findall(r"references/([\w\-]+\.md)", text)
        for ref in refs:
            target = self.root / "references" / ref
            if not target.exists():
                self.errors.append(f"Broken dispatch reference in SKILL.md: references/{ref}")

    # ── Orchestration ──

    def run(self) -> dict:
        self.check_files()
        self.check_directories()
        self.check_yaml()
        self.check_references()
        self.check_reference_coverage()
        self.check_scripts_executable()
        self.check_dispatch_links()

        healthy = len(self.missing) == 0 and len(self.errors) == 0
        return {
            "healthy": healthy,
            "missing": self.missing,
            "warnings": self.warnings,
            "errors": self.errors,
        }


# =========================
# CLI
# =========================
def main():
    parser = argparse.ArgumentParser(description="Check MindOS vault integrity")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        scanner = VaultScanner(Path(args.vault_root))
        result = scanner.run()
        print(json.dumps({"success": True, "data": result}, ensure_ascii=False))
        if not result["healthy"]:
            sys.exit(1)
    except Exception as e:
        logger.exception("Vault check failed")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
