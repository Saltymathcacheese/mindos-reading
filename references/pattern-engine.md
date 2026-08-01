# Pattern Engine (V0.2+)

Do NOT load or apply this reference unless version gate ≥ V0.2.

## Pattern Creation Requirements

A pattern requires EITHER:
- 2+ independent evidence items from DIFFERENT sources (e.g., 1 diary + 1 weread)
- 1 strong explicit user statement ("I've noticed I always do X when Y happens")

**Never create a pattern from:** a single sentence fragment, a temporary emotional state described in one entry, one unusual event, AI interpretation alone without raw evidence.

## Pattern YAML Format

```yaml
patterns:
  - id: "pat_XXX"
    name: "压力期信息消费偏移"
    description: "在学业压力增大期间，非教材类阅读量增加"
    status: "monitoring"          # monitoring|confirmed|active|dormant|archived|dismissed
    first_detected: "2026-08-01"
    last_updated: "2026-08-01"
    evidence:
      raw_evidence_ids: ["ev_001", "ev_002"]
    confidence: 0.40
    confidence_history:
      - {date: "2026-08-01", value: 0.40, reason: "首次检测"}
    decay:
      half_life_days: 90
      last_supported: "2026-08-01"
      min_confidence: 0.10
      auto_archive_after_days: 365
    effective_confidence: 0.40
    version_history:
      - {version: 1, date: "2026-08-01", confidence: 0.40, interpretation: "...", changed_by: "AI"}
    user_feedback: null
    user_correction: null
    related_actions: []
    tags: []
```

## Pattern Lifecycle

```
detected → monitoring → confirmed → active
                ↓            ↓
            dismissed     archived
                ↓
            dormant → archived → deleted
```

**Transitions:**
- detected → monitoring: 2+ independent evidence
- monitoring → confirmed: user feedback == confirmed OR confidence > 0.7
- confirmed → dormant: no new evidence for 90 days
- dormant → archived: no new evidence for 365 days
- any → dismissed: user feedback == dismissed
- dismissed → deleted: dismissed + 180 days elapsed (via garbage collection)

## Decay Formula

```
effective_confidence = confidence × 0.5^(days_since_last_supported / half_life_days)
```

Example: confidence 0.80, half_life 90 days. After 45 days without new evidence → effective = 0.80 × 0.707 = 0.566.

If `effective_confidence < 0.15`: pattern excluded from analysis output.
If `effective_confidence < min_confidence (0.10)`: marked dormant.
User confirmation resets `last_supported` to today.

## Presentation Rule

After presenting each pattern in a report, ask the user one of:
- "这个观察准确吗？" (if unconfirmed)
- "这个模式最近的 confidence 有变化。你的感受是？" (if confidence changed significantly)
- No question needed if already user-confirmed and stable.
