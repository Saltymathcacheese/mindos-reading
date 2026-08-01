# MindOS Handoff Protocol v1.0

Python ↔ Claude communication contract.

## analysis_request.json

Python produces this after building the Evidence Bundle.
Claude reads it, applies references/, and produces analysis_response.json.

### Structure

```json
{
  "protocol_version": "1.0",
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
  }
}
```

### Rules for Python
- Never include AI interpretations in this file
- Every fact must have a source field
- Confidence is L4 (human-verified) for all raw data

### Rules for Claude
- Read only the evidence section for facts
- Apply references/ for reasoning
- Never modify evidence — only interpret it
- Output analysis_response.json, not raw Markdown

---

## analysis_response.json

Claude produces this after cognitive analysis.
Python validates it, then renders to Markdown.

### Structure

```json
{
  "protocol_version": "1.0",
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
  "reflection": "你最近读的内容，是否影响了你的临床思维方式？"
}
```

### Rules for Claude
- Every layer must have confidence (L0-L4)
- reflection ≤ 60 characters
- evidence_used must cite at least one fact from the request
- No diagnostic language in any field
- No personality labels (even in "layer3" narrative)

### Rules for Python
- Validate against claude_response.schema.json before rendering
- Reject any response with missing layers or missing confidence
- Render to Markdown only after validation passes
