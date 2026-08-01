#!/usr/bin/env python3
"""
MindOS Runtime Controller — Unified entry point.

Commands:
    check       Vault integrity check
    status      Runtime state (version, diary count, patterns)
    validate    Schema + business rule validation
    analyze     Full pipeline: check → status → validate → fetch → state update

Usage:
    python scripts/mindos.py check
    python scripts/mindos.py status
    python scripts/mindos.py analyze

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

    def analyze(self) -> dict:
        """
        Full analysis pipeline:
        check → status → validate → fetch → context → request → [Claude] → validate_response → evaluate → report → prompt → state_update
        """
        pipeline: dict[str, dict] = {}

        # 1. Vault health
        vault_result = self.check()
        pipeline["vault"] = vault_result
        if not vault_result.get("healthy"):
            return {
                "success": False,
                "error": "Vault is not healthy — run 'mindos check' for details",
                "pipeline": pipeline,
            }

        # 2. Runtime state
        state = self.status()
        pipeline["state"] = state

        # 3. State validation
        validation = self.validate()
        pipeline["validation"] = validation

        # 4. Fetch WeRead data — write to file, then read it back
        weread_out = str(self.root / "7-System" / "raw_we_read.json")
        self._run("weread_fetch.py", ["--output", weread_out])
        # Read the file directly to avoid subprocess JSON parsing issues with large outputs
        import json as _json
        try:
            reading = _json.loads(Path(weread_out).read_text(encoding="utf-8"))
        except Exception:
            reading = {"success": False, "error": "Failed to read weread output"}
        pipeline["reading"] = reading

        # 5. Build Evidence Bundle
        context = self._run("analysis_context.py", [str(self.root)])
        pipeline["context"] = context

        # 6. Generate analysis request for Claude
        request_result = self._run("create_request.py", [str(self.root)])
        pipeline["request"] = request_result

        # 7. Generate report scaffold (Layer 1 pre-filled, Layer 2-3 placeholder)
        report = self._run("report_generator.py", [str(self.root)])
        pipeline["report"] = report

        # 8. Generate reflection prompt scaffold
        prompt = self._run("reflection_generator.py", [str(self.root)])
        pipeline["prompt"] = prompt

        # 9. Obsidian sync: wikilinks + broken link check
        sync_result = self._run("link_builder.py", [str(self.root)])
        pipeline["link_builder"] = sync_result

        graph_result = self._run("graph_builder.py", [str(self.root)])
        pipeline["graph_builder"] = graph_result

        # 11. Concept extraction
        concept_result = self._run("concept_extractor.py", [str(self.root)])
        pipeline["concept_extractor"] = concept_result

        # 12. Update state
        if reading.get("success") and "data" in reading:
            data = reading["data"]
            stats = data.get("stats", {})
            rt = stats.get("reading_time", {})
            total_hours = round(rt.get("total_seconds", 0) / 3600, 2)
            books_active = len(data.get("books_top10", []))
            notes_total = data.get("total_notes_all_books", 0)
            diary_count = state.get("diary_count", 0)

            update_result = self._run("state_update.py", [
                str(self.root),
                "--total-hours", str(total_hours),
                "--books-active", str(books_active),
                "--notes-total", str(notes_total),
                "--diary-count", str(diary_count),
            ])
            pipeline["state_update"] = update_result

        return {
            "success": True,
            "completed_at": datetime.now().isoformat(),
            "pipeline": pipeline,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="MindOS Runtime Controller")
    parser.add_argument("command", choices=["check", "status", "validate", "analyze"])
    parser.add_argument("--root", default=".", help="Vault root path")
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
            result = runtime.analyze()

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.exception("Runtime failed")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
