# Contributing to MindOS

Thank you for contributing to MindOS.

MindOS is an AI Agent system. Changes must protect:
- reliability
- interpretability
- user trust

---

# Before Modifying Code

Ask:

## 1. Which layer does this belong to?

Possible layers:
- Runtime
- Knowledge
- Identity
- Reasoning
- Calibration
- Evaluation
- Memory

If unclear: do not add.

---

# Architecture Rules

## Rule 1 — Do not put reasoning into Python

Bad:
```python
if user_reads_psychology:
    user_is_exploring_identity = True
```

Good — Python extracts:
```json
{"book_category": "psychology"}
```

Claude reasons using references.

## Rule 2 — New data requires schema

Any new object requires:
```
schemas/ + test
```

## Rule 3 — New feature requires test

Required:
```
Code → Schema → Test → Documentation
```

---

# Pull Request Requirements

Every change must include:

| Item | Description |
|------|-------------|
| Description | What changed? |
| Reason | Why needed? |
| Impact | Which modules affected? |
| Tests | What was verified? |

---

# Forbidden Changes

Do not:
- remove evidence system
- reduce confidence mechanism
- merge all scripts into one file
- hardcode API keys
- store raw private data unnecessarily
- create personality labels

---

# Code Style

Required:
- type hints
- logging
- error handling
- CLI support

Forbidden:
```python
print()
```

Use:
```python
logging.info()
```

---

# AI-Generated Code

AI generated code must:
- follow architecture
- include tests
- pass evaluation

Do not accept: "works on my machine"
