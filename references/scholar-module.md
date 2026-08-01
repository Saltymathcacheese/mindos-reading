# Scholar Module v2 — Personal Growth Lens with Optional Dental Identity

## Purpose

The Scholar Module provides a framework for understanding the user's intellectual and professional growth. It is NOT the only lens through which reading is viewed.

**Core shift from v1:** The user is a whole person first, a dental student second. The five dimensions now apply as a **tiered system** — some dimensions are always-on (general human growth), some are domain-gated (professional identity).

---

## Two-Tier Architecture

### Tier 1: Always-On (Personal Growth)

These dimensions apply to ALL reading analysis. They are about how a person learns and grows, regardless of field.

#### 1. Learning Efficacy (学习效能)

**What it tracks:** How effectively the user learns and self-regulates.

**Signals:**
- Reading about learning methods, productivity, habits
- Reading-time-to-study-time ratio
- Energy management signals (sleep, health reading)
- Diary mentions of study strategies

**Output language:**
- "本月学习方法类阅读占比 X%——你正在元认知层面优化'如何学习'。"
- "阅读时段集中在晚间，而日记中次日精力评分偏低。可能值得观察。"

**Always on.** Every learner has learning efficacy.

#### 2. Cognitive Breadth (认知广度)

**What it tracks:** The range and evolution of the user's intellectual interests.

**Signals:**
- Category diversity in reading
- Category shifts month-over-month
- Cross-domain theme emergence
- New domains appearing

**Output language:**
- "本月阅读覆盖 4 个领域：心理学、历史、医学、文学。认知广度健康。"
- "相比上月，历史类阅读从 5% 升至 25%——兴趣正在向人文学科扩展。"

**Always on.** Every person has an intellectual landscape that changes over time.

#### 3. Self-Understanding (自我理解)

**What it tracks:** The user's exploration of their inner world — emotions, relationships, values, identity.

**Signals:**
- Reading about psychology, relationships, personal growth
- Diary content themes
- Questions recorded in 4-Questions/
- Pattern detection around self-related themes

**Output language:**
- "本月自我探索类阅读占比 X%。你反复标记的内容涉及'关系中的自我'和'真实表达'——可能是一个正在浮现的探索方向。（L1）"
- **Never:** "你有关系焦虑" or "你正在通过阅读弥补情感缺失"

**Always on.** Self-understanding is a universal human project.

---

### Tier 2: Domain-Gated (Professional Identity)

These dimensions activate ONLY when the reading data directly supports them. They are hypotheses about professional growth, not default frameworks.

#### 4. Professional Identity (职业认同)

**Activation criteria (≥1 required):**
- Reading directly about medicine/dentistry/healthcare
- Reading about doctors' lives, medical memoirs
- Diary entries explicitly about career/future professional self
- Questions in 4-Questions/ about professional path

**What it tracks:** Transition from "student who studies dentistry" to "I am becoming a dentist."

**Output when active:**
- "本月出现医学叙事类阅读（《病房生死录》《学医七年》）——你正在通过他人的故事想象'成为医生是怎样的人生'。（L2）"

**Output when inactive:**
- "本月无明显职业认同信号。"

**Domain-gated.** Don't force it.

#### 5. Clinical Reasoning (临床思维)

**Activation criteria (≥2 required):**
- Reading directly about clinical practice, diagnosis, treatment
- Study notes showing causal chains, differential diagnosis thinking
- Diary entries discussing clinical scenarios or patient cases
- Reading about decision science AND user explicitly connects it to clinical thinking

**What it tracks:** Shift from memorizing facts to clinical reasoning.

**Output when active:**
- "牙周病学笔记中出现了完整的'检查→诊断→鉴别→治疗'链路。（L3）"

**Output when inactive:**
- "本月无明显临床推理信号。"

**Domain-gated.** Reading a psychology book does NOT automatically equal clinical reasoning development.

#### 6. Research Literacy (科研素养)

**Activation criteria (≥1 required):**
- Reading academic papers or research methodology books
- Notes that question or evaluate evidence quality
- Reading about statistics, study design, evidence-based practice

**Output when active:**
- "对研究方法的关注出现在笔记中——从'相信结论'到'追问证据'的转变。（L1）"

**Output when inactive:**
- "本月无明显科研素养信号。"

**Domain-gated.**

---

## Summary Table

| Dimension | Tier | Always On? | Activation | Confidence Range |
|-----------|------|-----------|-----------|-----------------|
| Learning Efficacy | 1 | Yes | Always | L2-L4 |
| Cognitive Breadth | 1 | Yes | Always | L3-L4 (factual) |
| Self-Understanding | 1 | Yes | Always | L1-L2 |
| Professional Identity | 2 | No | ≥1 criterion | L1-L3 |
| Clinical Reasoning | 2 | No | ≥2 criteria | L2-L4 |
| Research Literacy | 2 | No | ≥1 criterion | L1-L3 |

---

## Output Rules

1. **Always report Tier 1 dimensions** — these are about the person, not the profession.
2. **Only report Tier 2 when criteria are met** — "本月无明显X信号" is valid output.
3. **Never fabricate connections** — "读心理学 → 提升临床思维" is forbidden unless the user explicitly makes that connection in notes.
4. **Domain classification comes first** — use `reading-taxonomy.md` to assign domains, THEN apply scholar lens.
5. **The user is a person with a profession, not a profession that happens to be a person.**
