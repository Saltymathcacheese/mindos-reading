# Memory Compression (V0.3+, Quarterly)

Do NOT load or apply unless version gate ≥ V0.3.

## Purpose

Prevent graph explosion. 365 diary entries + 100 reading notes + 50 patterns + 200 reviews = unusable. Compression turns quantity into narrative.

## Compression Trigger

Every 90 days (quarterly). Input: 90 days of diary, reading notes, patterns, actions.

## Memory Value Score

```
Score = Impact × Repetition × Future_Relevance × Emotional_Weight
```

Each dimension 1-10:
- **Impact (×1.0):** How much did this change the user?
- **Repetition (×0.8):** How often does this theme recur?
- **Future Relevance (×1.2):** Is this likely to matter in the future? (higher weight)
- **Emotional Weight (×0.6):** Emotional significance (lower weight — avoid bias toward negatives)

Only high-scoring content survives compression. The rest is not deleted — just not loaded in future analysis sessions.

## Output: Core Memory File

**Path:** `10-Memory/核心记忆-YYYY.md`

**Structure:**
```markdown
# YYYY QX 核心记忆

## 这个季度的核心叙事
(AI-generated 2-3 sentence narrative. User confirms.)

## 关键事件
- 3-5 most impactful events

## 保留的 Evidence（最强 5 条）
1. [[source-link]] — "brief quote"
...

## 已知 Patterns 状态
| Pattern | 初始置信度 | 季末置信度 | 变化 |
|---------|-----------|-----------|------|

## 尝试过的 Actions
| Action | Result | What was learned |
|--------|--------|-----------------|

## 学到的经验
1-3 concise lessons
```

## Forgetting is a Feature

Not everything deserves permanent memory. The compression isn't loss — it's curation. What survives is what should survive.
