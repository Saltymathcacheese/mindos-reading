# MindOS Handoff Protocol v2.0

Python ↔ Claude cognitive exchange contract (v3.5+).

## Directory Structure

```
handoff/
├── incoming/        ← Python writes facts, Claude reads
│   └── analysis_request.json
├── outgoing/        ← Claude writes interpretation, Python reads
│   └── analysis_response.json
└── archive/         ← timestamped copies of completed exchanges
    └── 20260801-143000-analysis_request.json
```

## Protocol Flow

```
Phase 1 (Python):
    weread_fetch → analysis_context → create_request
    → handoff/incoming/analysis_request.json

Phase 2 (Claude):
    Read incoming/analysis_request.json
    Apply references/ (analysis-pipeline, scholar-module, confidence-system, etc.)
    Fill 3-layer analysis + reflection question
    → handoff/outgoing/analysis_response.json

Phase 3 (Python):
    validate_response → evaluator
    Gate: reject if safety violations or schema errors

Phase 4 (Python):
    report_generator → reflection_generator → link_builder → graph_builder → concept_extractor

Phase 5 (Python):
    state_update → memory_collector → calibration_engine

Archive:
    Move request + response to archive/ with timestamp
```

## analysis_request.json (Python → Claude)

```json
{
  "protocol_version": "2.0",
  "created_at": "2026-08-01T15:30:00",
  "mode": "V0.1",
  "task": {
    "type": "reading_analysis",
    "requirements": ["surface_analysis", "association_analysis", "narrative_analysis", "reflection_question"]
  },
  "evidence": {
    "reading": { ... },
    "diary": { ... }
  },
  "constraints": {
    "no_diagnosis": true,
    "no_personality_label": true,
    "pattern_creation": false,
    "max_reflection_chars": 60
  },
  "_handoff": {
    "direction": "Python → Claude",
    "instructions": "Read evidence. Apply references/. Fill response. Do NOT modify evidence."
  }
}
```

## analysis_response.json (Claude → Python)

```json
{
  "protocol_version": "2.0",
  "layer1": {
    "content": "本月阅读12小时，较上月增长20%……",
    "confidence": "L4"
  },
  "layer2": {
    "content": "心理学类阅读占比上升，可能与临床决策思维维度相关。",
    "confidence": "L1"
  },
  "layer3": {
    "content": "阅读方向正在从知识获取转向理解判断过程。",
    "confidence": "L1"
  },
  "evidence_used": [
    {"source": "WeRead API", "fact": "心理学类笔记从20%升至35%"}
  ],
  "reflection": "你最近读的内容，是否影响了你的临床思维方式？",
  "_handoff": {
    "direction": "Claude → Python",
    "instructions": "Python: validate this response, then render to Markdown."
  }
}
```

## Rules for Python

1. Never include AI interpretations in the request
2. Every fact must have a source field
3. Confidence L4 (human-verified) for all raw data
4. Validate response against `schemas/claude_response.schema.json` before rendering
5. Reject any response with missing layers or missing confidence
6. Render to Markdown only after validation passes
7. Archive completed exchanges with timestamps

## Rules for Claude

1. Read only the evidence section for facts
2. Apply references/ for reasoning
3. Never modify evidence — only interpret it
4. Every layer must have confidence (L0-L4)
5. reflection ≤ 60 characters
6. evidence_used must cite at least one fact from the request
7. No diagnostic language in any field
8. No personality labels (even in narrative layer3)
9. Output is analysis_response.json — NOT raw Markdown
