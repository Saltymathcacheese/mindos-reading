# MindOS

## Personal Cognitive Operating System

Version: 3.4.0

## Overview

MindOS is a personal cognitive growth system based on:

- Evidence collection
- Knowledge graph
- Identity-aware analysis
- Pattern detection
- Hypothesis tracking
- Self-calibration
- Evaluation framework

MindOS is NOT:

- A personality test
- A psychological diagnosis tool
- A life decision replacement system

MindOS observes:

"How does a person's knowledge, attention and behavior evolve over time?"

---

# Core Philosophy

## Evidence First

All insights follow:

```
Evidence
↓
Pattern
↓
Hypothesis
↓
User Validation
↓
Memory
```

The system never jumps directly from behavior to identity conclusions.

Example:

```
Wrong:
"You are a perfectionist."

Correct:
"Recent records show repeated high-standard goals.
This may indicate a preference for high-quality outcomes.
Confidence: L1.
Does this match your experience?"
```

---

# Architecture

```
                MindOS
                   |
             SKILL Router
                   |
    --------------------------------
    Runtime Layer              Knowledge Layer
         |                          |
   Data Collection          Knowledge Graph
         |                          |
   Evidence Store            Concept Nodes
                   |
             Reasoning Layer
                   |
    --------------------------------
    Identity   Pattern   Hypothesis
                   |
          Calibration Layer
                   |
          Evaluation Layer
                   |
             Memory Layer
```

---

# Features

## Reading Intelligence

Sources:
- WeRead
- Obsidian Notes

Capabilities:
- Reading statistics
- Book analysis
- Highlight extraction
- Reading trend detection
- Reflection generation

---

## Identity Layer

MindOS recognizes multiple identities:

- Professional Identity
- Learner Identity
- Explorer Identity
- Human Identity

The system does not assume one identity is dominant.

---

## Knowledge Graph

Transforms:

```
Book
↓
Concept
↓
Pattern
↓
Goal
```

Example:

```
Thinking Fast and Slow
    |
    ↓
Cognitive Bias
    |
    ↓
Decision Making
```

---

## Calibration

MindOS learns from corrections.

Every hypothesis can become:
- Confirmed
- Rejected
- Dormant

User feedback has higher priority than AI inference.

---

# Installation

## Requirements

Python >= 3.10

Install:

```bash
pip install -r requirements.txt
```

Configuration:

Copy `config.yaml.example` → `config.yaml`

Create `.env`:

```
WEREAD_API_KEY=your_key
MINDOS_VAULT_PATH=/path/to/vault
```

# Running

## Environment Check

```bash
python scripts/mindos.py check
```

Checks:
- directory structure
- dependencies
- configuration
- references
- schemas

## Status

```bash
python scripts/mindos.py status
```

Returns:
- version
- mode
- diary count
- pattern status

## Validation

```bash
python scripts/mindos.py validate
```

Runs:
- JSON Schema validation
- Business rule validation

## Full Analysis

```bash
python scripts/mindos.py analyze
```

Pipeline:

```
check → status → validate → fetch → analysis → report generation → state update → calibration
```

---

# Directory Structure

```
MindOS/
├── SKILL.md
├── references/
├── schemas/
├── scripts/
├── tests/
├── templates/
├── evaluation/
└── docs/
```

---

# Development Principles

## Python handles facts

Python should handle:
- API
- parsing
- validation
- files
- data transformation

Python should NOT:
- create psychological conclusions
- generate life advice
- replace reasoning layer

## References handle intelligence

Reasoning rules belong to `references/`, not `scripts/`.

---

# Testing

Run:

```bash
pytest
```

Before every release:

```
pytest → evaluation → benchmark
```

---

# Version

MindOS uses `Major.Minor.Patch`.

Example: `3.4.1`

---

# License

Personal Research Project
