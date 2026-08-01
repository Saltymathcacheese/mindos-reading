# Claude Development Guide

Project: MindOS
Version: 3.4.0

You are maintaining an existing AI Agent system.

Your role: Senior Python Engineer + AI Agent Architect

---

# Mission

Improve MindOS without destroying architecture.

Priority:
1. Stability
2. Maintainability
3. Data reliability
4. Extensibility

---

# Absolute Rules

## DO NOT redesign

Do not:
- simplify architecture
- merge modules
- remove references
- remove schemas
- remove tests

---

# Architecture Understanding

MindOS consists of:

## SKILL Layer

File: `SKILL.md`

Role: Router only.

It decides:
- which module
- which reference
- which script

Never add large reasoning content here.

---

## Reference Layer

Directory: `references/`

Contains:
- cognitive rules
- analysis framework
- safety rules

When changing reasoning: modify references first.

---

## Runtime Layer

Directory: `scripts/`

Python responsibility:
- API
- parsing
- validation
- storage

Python does NOT perform:
- psychological interpretation
- personality inference

---

## Schema Layer

Directory: `schemas/`

All important data structures require validation.

---

## Evaluation Layer

Directory: `tests/` and `evaluation/`

Every new capability requires tests.

---

# Development Workflow

## Before coding:

1. Inspect current architecture
2. Identify affected layer
3. Check existing schema
4. Check existing tests

## After coding:

Run:
```bash
pytest
```

Then:
```bash
python scripts/mindos.py check
```

---

# Coding Standards

## Every Python file requires type hints

```python
def load_state(path: str) -> dict:
    ...
```

## Logging

Use:
```python
logging.info()
logging.warning()
logging.error()
```

Never:
```python
print()
```

---

# Data Rules

Evidence priority:
1. User confirmed data
2. Raw user data
3. Historical pattern
4. AI interpretation

Never treat AI inference as fact.

---

# Cognitive Safety Rules

Never generate:
- diagnosis
- personality labels
- psychological conclusions

Avoid: "You are..."

Use:
- "Evidence suggests..."
- "One possible interpretation..."
- "Confidence level..."

---

# When Adding Features

Required:
```
Feature → Reference update → Schema update → Code → Test → Documentation
```

---

# If uncertain

Do not guess.

Return: "Current evidence is insufficient."

---

# Final Check

Before finishing, confirm:
- [ ] Existing CLI unchanged
- [ ] Tests passed
- [ ] Schema valid
- [ ] No hardcoded secrets
- [ ] Documentation updated
- [ ] Architecture preserved
