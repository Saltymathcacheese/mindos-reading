#!/usr/bin/env python3
"""
MindOS Runtime Controller — Unified entry point (v3.5).

Commands:
    check       Vault integrity check
    status      Runtime state (version, diary count, patterns)
    validate    Schema + business rule validation
    analyze     Full Agent Loop: data → cognition → verify → render → learn

The `analyze` command now runs the complete v3.5 pipeline via analysis_runner.py.
Phase 2 (Cognition) is a GATE — Claude must fill the response via the handoff protocol.
Phases 3-5 auto-continue once the response is ready.

Usage:
    python scripts/mindos.py check
    python scripts/mindos.py status
    python scripts/mindos.py analyze
    python scripts/mindos.py analyze --phase data     # run only data collection
    python scripts/mindos.py analyze --phase verify    # resume from verification

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("mindos.runtime")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


class MindOSRuntime:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.scripts_dir = self.root / "scripts"

    def _run(self, script: str, args: list[str] | None = None) -> dict:
        """Run a scripts/*.py with subprocess, return parsed JSON or error dict."""
        script_path = self.scripts_dir / script
        if not script_path.exists():
            raise RuntimeError(f"Script not found: {script}")

        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        logger.info("Running %s", script)
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip() or "unknown error"
            raise RuntimeError(f"{script} failed: {stderr}")

        try:
            # Parse JSON from stdout, skipping logging noise lines
            for line in result.stdout.strip().splitlines():
                stripped = line.strip()
                if stripped.startswith('{'):
                    return json.loads(stripped)
            return {"raw": result.stdout}
        except json.JSONDecodeError:
            return {"raw": result.stdout}

    # ── Commands ──

    def check(self) -> dict:
        """Vault integrity check. Returns data dict with 'healthy' key.
        Gracefully handles missing scripts/ — the vault is unhealthy if its own tools are absent."""
        try:
            result = self._run("vault_check.py", [str(self.root)])
            return result.get("data", result)
        except RuntimeError:
            return {"healthy": False, "missing": ["scripts/vault_check.py"], "warnings": [], "errors": ["vault_check.py not found — vault runtime is incomplete"]}

    def status(self) -> dict:
        """Runtime state: version, diary count."""
        return self._run("preflight.py", [str(self.root)])

    def validate(self) -> dict:
        """State validation: schema + business rules."""
        return self._run("validate_state.py", [str(self.root)])

    def analyze(self, phase: str = "full") -> dict:
        """
        Full v3.5 Agent Loop via analysis_runner.py.

        Phases:
            full       = data → cognition → verify → render → learn
            data       = check → status → validate → fetch → context → request
            cognition  = check if Claude filled response (gate)
            verify     = validate response against schema + safety rules
            render     = report → reflection → wikilinks → graph → concepts
            learn      = state update → memory collection → calibration

        Returns pipeline result dict with status, outputs, and phase details.
        """
        return self._run("analysis_runner.py", [str(self.root), "--phase", phase])


def main() -> None:
    parser = argparse.ArgumentParser(description="MindOS Runtime Controller v3.5")
    parser.add_argument("command", choices=["check", "status", "validate", "analyze"])
    parser.add_argument("--root", default=".", help="Vault root path")
    parser.add_argument("--phase", default="full",
                        choices=["full", "data", "cognition", "verify", "render", "learn"],
                        help="Pipeline phase (analyze command only)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    runtime = MindOSRuntime(Path(args.root))

    try:
        if args.command == "check":
            result = runtime.check()
        elif args.command == "status":
            result = runtime.status()
        elif args.command == "validate":
            result = runtime.validate()
        else:
            result = runtime.analyze(phase=args.phase)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.exception("Runtime failed")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
