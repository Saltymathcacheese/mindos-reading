# Confidence & Evidence System

## Confidence Levels

| Level | Range | Label | Condition | Display Rule |
|-------|-------|-------|-----------|-------------|
| L0 | 0.0-0.2 | 推测 | Single observation, no cross-validation | Must flag: "这只是一个初步推测" |
| L1 | 0.2-0.4 | 初步信号 | 2+ occurrences in same data source | |
| L2 | 0.4-0.6 | 中等可信 | Multiple occurrences across 2+ sources | |
| L3 | 0.6-0.8 | 较高可信 | Cross-source + user confirmed + sustained | |
| L4 | 0.8-1.0 | 确认模式 | User explicitly confirmed, multiple cycles | |

## Evidence Data Priority (Hierarchy)

1. **Direct user confirmation** — highest weight. "Yes, that's accurate."
2. **Cross-source convergence** — reading + diary + learning data all agree
3. **Repeated single-source** — same signal 3+ times in one source
4. **Single occurrence** — lowest. Initiates monitoring only, no pattern creation.

## Raw Evidence Format (V0.2+)

Each evidence record stored in `7-System/raw_evidence/` as YAML:

```yaml
evidence_id: "ev_001"
date: "2026-08-01"
source_type: "diary"         # diary | weread_note | weread_bookmark | learning_log
source_file: "[[2026-08-01-日记]]"
raw_text: "原始引用，不可被AI改写，≤80 chars"
ai_interpretation: "AI对这一条的理解"
interpretation_confidence: 0.0  # 0-1
user_feedback: null           # confirmed | corrected | rejected
user_correction: null         # user's own interpretation
pattern_link: null            # associated pattern_id
extracted_at: "2026-08-01"
```

**Critical rule:** `raw_text` is the original quote — never rewritten by AI. `ai_interpretation` and `raw_text` must always be shown together.

## Anti-Overfitting Rules

1. A pattern requires at least 2 independent evidence points from different sources before appearing in any report (OR 1 explicit user statement).
2. Every pattern in output MUST include its confidence level.
3. Every pattern in output MUST ask for user validation.
4. A user "no" immediately drops confidence by 0.4; if resulting confidence < 0.2, move to dismissed.
5. Never create a pattern from a single diary entry alone.
6. If the user hasn't written any diaries, ALL interpretations from reading data alone are capped at L1.
