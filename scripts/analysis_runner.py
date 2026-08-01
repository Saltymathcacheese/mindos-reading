#!/usr/bin/env python3
"""
MindOS analysis_runner.py — Agent Loop Orchestrator (v3.5).

The missing link between Python facts and Claude cognition.
Does NOT call any LLM API. Uses the handoff protocol:

    Evidence Package
        ↓
    handoff/incoming/analysis_request.json    [Python → Claude]
        ↓
    [Claude reads request + references, produces response]
        ↓
    handoff/outgoing/analysis_response.json   [Claude → Python]
        ↓
    validate → render → wikilinks → graph → memory → state → calibrate

Usage:
    python scripts/analysis_runner.py [vault_root]

Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("mindos.runner")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# ============================================================
# Handoff Protocol
# ============================================================
class HandoffProtocol:
    """Manages the Python ↔ Claude cognitive handoff.

    incoming/  = Python writes facts, Claude reads
    outgoing/  = Claude writes interpretation, Python reads
    archive/   = timestamped copies of completed exchanges
    """

    def __init__(self, vault: Path):
        self.incoming = vault / "handoff" / "incoming"
        self.outgoing = vault / "handoff" / "outgoing"
        self.archive = vault / "handoff" / "archive"
        for d in (self.incoming, self.outgoing, self.archive):
            d.mkdir(parents=True, exist_ok=True)

    def write_request(self, data: dict) -> Path:
        path = self.incoming / "analysis_request.json"
        data["_handoff"] = {
            "direction": "Python → Claude",
            "created_at": datetime.now().isoformat(),
            "instructions": "Read evidence. Apply references/. Fill response. Do NOT modify evidence.",
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def read_request(self) -> dict | None:
        path = self.incoming / "analysis_request.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def write_response(self, data: dict) -> Path:
        path = self.outgoing / "analysis_response.json"
        data["_handoff"] = {
            "direction": "Claude → Python",
            "created_at": datetime.now().isoformat(),
            "instructions": "Python: validate this response, then render to Markdown.",
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def read_response(self) -> dict | None:
        path = self.outgoing / "analysis_response.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def archive_exchange(self) -> None:
        """Move current request + response to archive with timestamp."""
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        for fname in ("analysis_request.json", "analysis_response.json"):
            src_in = self.incoming / fname
            src_out = self.outgoing / fname
            dst = self.archive / f"{ts}-{fname}"
            for src in (src_in, src_out):
                if src.exists():
                    shutil.copy2(src, dst)
                    if "request" in fname:
                        src.unlink()  # clean incoming after archive


# ============================================================
# Pipeline Step Runner
# ============================================================
class StepRunner:
    """Runs individual scripts/*.py steps as subprocesses, collecting results."""

    def __init__(self, scripts_dir: Path):
        self.scripts_dir = scripts_dir

    def run(self, script: str, args: list[str] | None = None) -> dict:
        script_path = self.scripts_dir / script
        if not script_path.exists():
            return {"success": False, "error": f"Script not found: {script}"}

        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        logger.info("Running %s", script)
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip() or "unknown error"
            return {"success": False, "error": f"{script} failed: {stderr}"}

        # Parse JSON from stdout
        for line in result.stdout.strip().splitlines():
            stripped = line.strip()
            if stripped.startswith("{"):
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    continue
        return {"success": True, "raw": result.stdout}


# ============================================================
# Analysis Runner — Main Orchestrator
# ============================================================
class AnalysisRunner:
    """Orchestrates the full v3.5 Agent Loop.

    Pipeline phases:
      Phase 1 — Data:     check → status → validate → fetch → context → request
      Phase 2 — Cognition: [Claude fills response via SKILL.md workflow]
      Phase 3 — Verify:    validate_response → evaluate
      Phase 4 — Render:    report → reflection → wikilinks → graph → concepts
      Phase 5 — Learn:     memory → state_update → calibration
    """

    def __init__(self, vault: Path, scripts_dir: Path | None = None):
        self.vault = vault.resolve()
        # scripts_dir defaults to the actual scripts/ directory (sibling of this file)
        if scripts_dir is None:
            scripts_dir = Path(__file__).resolve().parent
        self.scripts = StepRunner(scripts_dir)
        self.handoff = HandoffProtocol(vault)

    # ── Phase 1: Data Collection ──

    def phase1_data(self) -> dict:
        """Collect all facts. Returns pipeline results dict."""
        results: dict[str, dict] = {}
        vault_str = str(self.vault)

        # 1. Vault health check
        r = self.scripts.run("vault_check.py", [vault_str])
        results["vault"] = r
        if not r.get("healthy") and not r.get("success"):
            return {"phase": "data", "success": False, "error": "Vault unhealthy", "results": results}

        # 2. Runtime state
        results["state"] = self.scripts.run("preflight.py", [vault_str])

        # 3. State validation
        results["validation"] = self.scripts.run("validate_state.py", [vault_str])

        # 4. Fetch WeRead data
        weread_out = str(self.vault / "7-System" / "raw_we_read.json")
        fetch = self.scripts.run("weread_fetch.py", ["--output", weread_out])
        results["fetch"] = fetch
        # Read the file directly for reliable data access
        weread_path = self.vault / "7-System" / "raw_we_read.json"
        try:
            results["reading"] = json.loads(weread_path.read_text(encoding="utf-8"))
        except Exception:
            results["reading"] = {"success": False, "error": "Failed to read weread output"}

        # 5. Build Evidence Bundle
        results["context"] = self.scripts.run("analysis_context.py", [vault_str])

        # 6. Generate handoff request for Claude
        results["request"] = self.scripts.run("create_request.py", [vault_str])

        return {"phase": "data", "success": True, "results": results}

    # ── Phase 2: Cognition (Claude fills response) ──

    def phase2_cognition(self) -> dict:
        """Check if Claude has filled the response file.

        This phase is a GATE — it waits for Claude (via SKILL.md workflow)
        to read handoff/incoming/analysis_request.json and write
        handoff/outgoing/analysis_response.json.

        Returns success=True only if response exists and is valid.
        """
        response = self.handoff.read_response()
        if not response:
            return {
                "phase": "cognition",
                "success": False,
                "status": "awaiting_claude",
                "message": "handoff/outgoing/analysis_response.json not found. "
                           "Claude must fill the response by reading handoff/incoming/analysis_request.json "
                           "and applying references/. Then write the result to handoff/outgoing/analysis_response.json.",
                "next_action": "Run SKILL.md Step 2 (Cognitive Fill) to generate the response.",
            }

        # Basic structure check (doesn't replace full validation in Phase 3)
        required = ["layer1", "layer2", "layer3", "reflection", "evidence_used"]
        missing = [k for k in required if k not in response]
        if missing:
            return {
                "phase": "cognition",
                "success": False,
                "status": "incomplete_response",
                "missing_fields": missing,
                "message": f"Response missing required fields: {missing}",
            }

        return {
            "phase": "cognition",
            "success": True,
            "status": "response_ready",
            "mode": response.get("protocol_version", "1.0"),
        }

    # ── Phase 3: Verify ──

    def phase3_verify(self) -> dict:
        """Validate Claude's response against schema + safety rules."""
        vault_str = str(self.vault)

        # Validate response
        response_path = str(self.vault / "handoff" / "outgoing" / "analysis_response.json")
        schema_path = str(self.vault / "schemas" / "claude_response.schema.json")
        validation = self.scripts.run("validate_response.py", [
            "--input", response_path,
            "--schema", schema_path,
        ])

        # Run evaluators (safety + evidence checks)
        eval_result = self.scripts.run("evaluator.py", [vault_str])

        return {
            "phase": "verify",
            "success": validation.get("success", False),
            "validation": validation,
            "evaluation": eval_result,
        }

    # ── Phase 4: Render ──

    def phase4_render(self) -> dict:
        """Render validated response to Obsidian markdown, build links + graph."""
        vault_str = str(self.vault)
        results: dict[str, dict] = {}

        # Generate report markdown (now with Claude-filled content)
        results["report"] = self.scripts.run("report_generator.py", [vault_str])

        # Generate reflection prompt
        results["prompt"] = self.scripts.run("reflection_generator.py", [vault_str])

        # Inject wikilinks
        results["links"] = self.scripts.run("link_builder.py", [vault_str])

        # Build knowledge graph
        results["graph"] = self.scripts.run("graph_builder.py", [vault_str])

        # Extract concepts
        results["concepts"] = self.scripts.run("concept_extractor.py", [vault_str])

        return {"phase": "render", "success": True, "results": results}

    # ── Phase 5: Learn ──

    def phase5_learn(self, phase1_results: dict) -> dict:
        """Update state, compress memories, calibrate model."""
        vault_str = str(self.vault)
        results: dict[str, dict] = {}

        # State update
        reading_data = phase1_results.get("reading", {})
        state_info = phase1_results.get("state", {})
        if reading_data.get("success") and "data" in reading_data:
            data = reading_data["data"]
            stats = data.get("stats", {})
            rt = stats.get("reading_time", {})
            total_hours = round(rt.get("total_seconds", 0) / 3600, 2)
            books_active = len(data.get("books_top10", []))
            notes_total = data.get("total_notes_all_books", 0)
            diary_count = state_info.get("diary_count", 0)

            results["state_update"] = self.scripts.run("state_update.py", [
                vault_str,
                "--total-hours", str(total_hours),
                "--books-active", str(books_active),
                "--notes-total", str(notes_total),
                "--diary-count", str(diary_count),
            ])
        else:
            results["state_update"] = {"success": False, "error": "No reading data for state update"}

        # Memory collection
        results["memory"] = self.scripts.run("memory_collector.py", [vault_str])

        # Calibration
        results["calibration"] = self.scripts.run("calibration_engine.py", [vault_str])

        return {"phase": "learn", "success": True, "results": results}

    # ── Full Pipeline ──

    def run_full(self) -> dict:
        """Execute the complete v3.5 Agent Loop."""
        pipeline: dict[str, dict] = {}
        started_at = datetime.now()

        # Phase 1: Data Collection
        logger.info("=== Phase 1: Data Collection ===")
        p1 = self.phase1_data()
        pipeline["data"] = p1
        if not p1["success"]:
            return self._fail("Phase 1 (Data) failed", pipeline, started_at)

        # Phase 2: Cognition Gate
        logger.info("=== Phase 2: Cognition ===")
        p2 = self.phase2_cognition()
        pipeline["cognition"] = p2
        if not p2["success"]:
            return {
                "success": False,
                "status": "awaiting_cognition",
                "message": p2.get("message", "Claude response required"),
                "pipeline": pipeline,
                "started_at": started_at.isoformat(),
                "completed_at": datetime.now().isoformat(),
            }

        # Phase 3: Verification
        logger.info("=== Phase 3: Verification ===")
        p3 = self.phase3_verify()
        pipeline["verify"] = p3
        if not p3["success"]:
            return self._fail("Phase 3 (Verify) failed — response has errors", pipeline, started_at)

        # Phase 4: Render
        logger.info("=== Phase 4: Render ===")
        p4 = self.phase4_render()
        pipeline["render"] = p4

        # Phase 5: Learn
        logger.info("=== Phase 5: Learn ===")
        p5 = self.phase5_learn(p1["results"])
        pipeline["learn"] = p5

        # Archive completed exchange
        self.handoff.archive_exchange()

        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()

        # Collect output paths for the user
        today = datetime.now().strftime("%Y-%m-%d")
        outputs = {
            "report": str(self.vault / "6-Reviews" / f"{today}-阅读分析.md"),
            "reflection": str(self.vault / "0-Inbox" / f"{today}-反思引导.md"),
            "knowledge_graph": str(self.vault / "7-System" / "knowledge_graph.json"),
            "analysis_context": str(self.vault / "7-System" / "analysis_context.json"),
        }

        return {
            "success": True,
            "status": "complete",
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_seconds": duration,
            "outputs": outputs,
            "pipeline": pipeline,
        }

    def _fail(self, error: str, pipeline: dict, started_at: datetime) -> dict:
        return {
            "success": False,
            "status": "failed",
            "error": error,
            "pipeline": pipeline,
            "started_at": started_at.isoformat(),
            "completed_at": datetime.now().isoformat(),
        }


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="MindOS Analysis Runner — v3.5 Agent Loop")
    parser.add_argument("vault_root", nargs="?", default=".")
    parser.add_argument("--phase", choices=["data", "cognition", "verify", "render", "learn", "full"],
                        default="full", help="Run specific phase only (default: full pipeline)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    vault = Path(args.vault_root)
    runner = AnalysisRunner(vault)

    try:
        if args.phase == "data":
            result = runner.phase1_data()
        elif args.phase == "cognition":
            result = runner.phase2_cognition()
        elif args.phase == "verify":
            result = runner.phase3_verify()
        elif args.phase == "render":
            result = runner.phase4_render()
        elif args.phase == "learn":
            # Learn phase needs phase1 data — run it first
            p1 = runner.phase1_data()
            if not p1["success"]:
                result = runner._fail("Phase 1 failed — cannot run learn phase", {"data": p1}, datetime.now())
            else:
                result = runner.phase5_learn(p1["results"])
        else:
            result = runner.run_full()

        print(json.dumps(result, ensure_ascii=False, indent=2))

        if not result.get("success"):
            sys.exit(1)

    except Exception as e:
        logger.exception("Analysis runner failed")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
