# MindOS Repository Specification v3.4

## Identity

MindOS is a Personal Cognitive Operating System — NOT a psychological diagnosis tool, personality evaluator, or chatbot. It is a layered agent runtime for long-term cognitive growth tracking.

## Architecture (8 frozen layers)

```
SKILL.md (Router)
    │
    ├── Runtime Layer (scripts/)
    │   Data pipeline — API, state, validation
    │
    ├── Knowledge Layer (2-Knowledge/)
    │   Graph + concepts + books
    │
    ├── Identity Layer (references/identity-layer.md)
    │   5 dimensions, domain router, person-first
    │
    ├── Reasoning Layer (references/)
    │   Evidence → Pattern → Hypothesis
    │
    ├── Calibration Layer (7-System/calibration.yaml)
    │   Prediction → Feedback → Adjust
    │
    ├── Evaluation Layer (evaluation/)
    │   Cognitive quality tests, benchmark
    │
    └── Memory Layer (10-Memory/)
        Compress + decay, not preserve all
```

## Module Responsibilities

| Module | Location | Responsibility | Forbidden |
|--------|----------|---------------|-----------|
| Router | SKILL.md | Trigger dispatch, reference loading | Storing knowledge |
| References | references/ | Cognitive rules ("how to think") | Code execution |
| Scripts | scripts/ | Deterministic computation | Generating insights |
| Schemas | schemas/ | Data contracts | Business logic |
| Tests | tests/ | Behavior drift prevention | Implementation-only tests |

## Entry Point

```bash
python scripts/mindos.py check      # Environment health
python scripts/mindos.py status     # Current state
python scripts/mindos.py validate   # State validation
python scripts/mindos.py analyze    # Full pipeline
python scripts/mindos.py memory     # Memory compression
python scripts/benchmark.py         # System benchmark
```

## Environment

```bash
# Required
export WEREAD_API_KEY="wrk-xxxxxxxx"

# Install
pip install -r requirements.txt --break-system-packages

# Init
python scripts/init.py --vault .
```

## Modification Protocol

```
You are maintaining MindOS v3.4.
1. Do not change directory structure
2. Do not change data semantics
3. Do not delete existing functionality
4. New features must add a schema
5. New logic must add a test
6. Python handles facts, not cognitive reasoning
7. References handle cognitive frameworks
8. Run pytest after all changes
```

## Safety Boundaries

- No personality labels ("you are a perfectionist")
- No diagnostic language ("you may have anxiety")
- No forced professional connections to non-medical reading
- Evidence before interpretation
- Confidence (L0-L4) on every interpretation
- "No signal" is valid output

## Versioning

Semantic: `MAJOR.MINOR.PATCH`
- Patch: bug fixes
- Minor: new modules
- Major: architecture changes

## Current Baseline

v3.4.0 — Architecture Freeze
- 28 scripts (4,127 lines)
- 12 references (1,039 lines)
- 5 JSON schemas
- 19 cognitive test cases
- 102 unit tests
- Grade A benchmark
