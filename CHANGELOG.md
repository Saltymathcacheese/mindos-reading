# Changelog

## 3.4.0 (2026-08-01) — Architecture Freeze

### Added
- Evaluation layer with 19 cognitive test cases (safety, reading, pattern)
- `scripts/evaluator.py` — cognitive quality evaluator
- `scripts/benchmark.py` — full system benchmark (A-F grade)
- `evaluation/test_cases/` — reading, safety, pattern case definitions
- `.gitignore` — vault artifacts excluded from version control

### Changed
- Scholar Module v2: domain-first classification, 2-tier (person-first / profession-gated)
- Identity Layer: 5 dimensions with activation criteria
- `references/reading-taxonomy.md` — 6-domain classification system
- `SKILL.md` — updated for identity-aware routing

### Frozen
- 8 architecture layers with documented boundaries
- 4 freeze rules for future development
- Repository specification established

### Metrics
- 28 Python scripts (4,127 lines)
- 12 reference documents (1,039 lines)
- 5 JSON schemas
- 102 unit tests (zero failures)
- Grade A benchmark

---

## 3.3.0 (2026-08-01) — Self-Calibration Layer

### Added
- `7-System/calibration.yaml` — accuracy tracking, confidence multiplier, bias detection
- `7-System/prediction_history.yaml` — testable predictions with validation windows
- `7-System/feedback_history.yaml` — user corrections (highest-weight data)
- `scripts/calibration_engine.py` — accuracy computation + multiplier adjustment
- `scripts/prediction_tracker.py` — prediction lifecycle management
- `scripts/feedback_processor.py` — user feedback ingestion
- `7-System/relations.yaml` — 7 typed knowledge graph relations

### Changed
- Safe mode triggers refined: accuracy < 0.5, false positive rate > 0.4, corrections > 5
- Confidence and Accuracy separated as independent metrics

---

## 3.2.0 (2026-08-01) — Knowledge Graph Layer

### Added
- `scripts/concept_extractor.py` — extract recurring concepts from highlights
- `scripts/graph_builder.py` — typed knowledge graph construction
- `2-Knowledge/Concepts/` — concept node directory
- `Templates/concept.md` — concept node template
- `7-System/Knowledge Dashboard.md` — Dataview dashboard

---

## 3.1.0 (2026-08-01) — Obsidian Graph Layer

### Added
- `scripts/link_builder.py` — automatic [[wikilink]] injection
- `scripts/obsidian_sync.py` — broken link detection
- `scripts/graph_indexer.py` — node/edge statistics
- Typed frontmatter for all generated files (book, review, pattern, goal, memory)

---

## 3.0.0 (2026-08-01) — Real Deployment

### Added
- WeRead API integration (weread_fetch.py) with retry + backoff
- First end-to-end pipeline run (vault_check → state_update)
- `handoff/` protocol (analysis_request.json ↔ analysis_response.json)
- `7-System/bugs.yaml` — bug tracking

### Fixed
- `bug_001`: mindos.py subprocess JSON parsing → file-based I/O
- `bug_002`: diary template {{date}} → Obsidian Templater syntax

---

## 2.6.0 (2026-08-01) — Production Release

### Added
- `scripts/init.py` — one-command vault initializer
- `.env.example` — environment config template
- `config.yaml.example` — runtime config template

---

## 2.5.0 (2026-08-01) — Memory Evolution

### Added
- `scripts/memory_collector.py` — gather 90-day content for compression
- `scripts/memory_scorer.py` — weighted value scoring (impact×.30 + repetition×.25 + future×.35 + emotion×.10)
- `scripts/memory_validator.py` — safety validation for memory entries
- `schemas/memory.schema.json`

---

## 2.4.0 (2026-08-01) — Self-Calibration (design)

### Added
- Calibration engine concept (prediction → feedback → confidence adjustment)
- Safe mode design

---

## 2.3.0 (2026-08-01) — Cognitive Bridge

### Added
- `scripts/analysis_context.py` — Evidence Bundle builder
- `scripts/report_generator.py` — Layer 1 scaffold
- `scripts/reflection_generator.py` — daily prompt scaffold
- `scripts/create_request.py` — handoff request generator
- `scripts/validate_response.py` — Claude output validator
- `schemas/claude_response.schema.json`

---

## 2.2.0 (2026-08-01) — Unified Entry

### Added
- `scripts/mindos.py` — Runtime Controller (check, status, validate, analyze)

---

## 2.1.0 (2026-08-01) — Stability Fixes

### Changed
- `state_update.py`: YAMLStateManager class replaces module-level YAML instance
- `weread_fetch.py`: `get_notebooks` → `_get_notebooks_page` + `fetch_all_notebooks`
- `vault_check.py`: extended REQUIRED_DIRS, added check_scripts_executable, check_reference_coverage, check_dispatch_links

### Added
- `scripts/validate_state.py` — dual-layer validation (JSON Schema + business rules)

---

## 2.0.0 (2026-08-01) — Initial Implementation

### Added
- Vault directory structure (0-Inbox through 10-Memory)
- 12 YAML state machines (analysis_state, cognitive_patterns, hypotheses, interaction_model, interaction_state, effort_budget, triggers, reading_influence, scholar_profile, metrics, privacy, lifecycle)
- 8 Obsidian templates
- SKILL.md (initial version)
- 75 unit tests
