# Output Templates — Exact Formats

## Output 1: Reading Analysis

**Path:** `6-Reviews/YYYY-MM-DD-阅读分析.md`

**Frontmatter:**
```yaml
---
title: "YYYY-MM-DD 阅读分析"
date: YYYY-MM-DD
type: reading-analysis
period: "30天"
tags: [reading, analysis]
data_source: "微信读书 API"
confidence_note: "首次分析，所有解释性结论为 L0-L1"  # Only for first run
---
```

**Sections (in order):**

### 📊 阅读统计
Table: 指标 | 数值 | 备注. Include: total reading time (hours+minutes), active books, reading days, notes total, trend arrow. If compare is available, show ↑/↓ %.

### 📖 笔记库存全景
Top 10 books table: 书 | 类别 | 划线 | 想法 | 书签 | 总笔记 | 状态

### 🏷 书架组织
Brief paragraph on 书单 names and what they reveal about mental organization. With context from previously seen data if available.

### 🧠 笔记主题分析
From highlight samples, extract 2-3 cross-cutting themes. Each theme: name + evidence (actual highlight quotes, ≤50 chars each). Show the connection between different books under the same theme.

### 🎓 学术成长视角
Scholar reclassification table: weread category → scholar dimension.
Signal by dimension: what each of the 5 dimensions shows this month. "No signal" if no data.

### ⚡ 本月值得注意的信号
One notable change or observation. Can be null — say "本月无显著异常信号" if nothing stands out. Always include confidence level.

---

## Output 2: Reflection Prompt

**Path:** `0-Inbox/YYYY-MM-DD-反思引导.md`

```markdown
---
date: YYYY-MM-DD
type: daily-prompt
source: reading-analysis
---

# 今天的反思

（ONE question, ≤50 words. Open-ended, connects reading to life, not a survey.）

（Optional context: ≤80 words, explains why this question emerged from the data.）
```

**Bad:** "你最近读书多吗？为什么？"
**Good:** "你在41本书里留下了1698条笔记。如果让你用一句话总结：这些书加在一起，你在找什么？"

---

## Output 3: State Update

Update `7-System/analysis_state.yaml` after every run:

```yaml
last_analysis:
  date: "YYYY-MM-DD"
  session_id: "mindos-<random>"
  mode: "V0.1"

# Update reading metrics:
metrics:
  reading:
    total_hours_30d: {value: <float>, trend: <up|down|stable>, confidence: 1.0}
    books_active: {value: <int>, trend: stable, confidence: 1.0}
    notes_total: {value: <int>, trend: stable, confidence: 1.0}

# Update data sufficiency:
data_sufficiency:
  diary_entries_total: <count from 1-Experiences/>
```

If `scripts/state_update.py` is available, run it with the computed values. Otherwise, edit the YAML file directly.
