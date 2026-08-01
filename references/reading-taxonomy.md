# Reading Taxonomy — MindOS Domain Classification

## Purpose

Classify every book/reading into a primary domain BEFORE applying any identity lens.
This prevents the system from forcing every book through a single narrow frame (e.g., "how does this improve clinical reasoning?").

## Core Principle

**Domain first, identity lens second — and only when evidence supports it.**

A book about history is about history. A novel is a novel. Only a dental textbook is directly about dentistry. The system must respect what the book IS before asking what it MEANS for the user.

---

## Six Reading Domains

### 1. Professional Growth (专业成长)

Books that directly relate to the user's field of study or work.

**Criteria:** Content is explicitly about dentistry, medicine, clinical practice, or healthcare systems.

**Examples:**《牙周病学》《从骨至筋》《病房生死录》《学医七年》

**MindOS tags:** `domain: professional` `topic: dentistry|medicine|clinical`

**When to connect to Scholar Lens:** Always — this is the domain where the five scholar dimensions naturally apply.

---

### 2. General Cognition (通识认知)

Books about how the mind works, how we think, how we make decisions, how we learn.

**Criteria:** Content addresses cognitive processes, judgment, reasoning, learning mechanisms.

**Examples:**《思考，快与慢》《掌控习惯》《海绵阅读法》《我们为什么要睡觉？》

**MindOS tags:** `domain: cognition` `topic: decision|learning|memory|bias`

**When to connect to Scholar Lens:** Only when the user's notes explicitly bridge to clinical scenarios. Otherwise: "这是关于人类认知的通识阅读。"

---

### 3. Humanities & Culture (人文素养)

Books about history, philosophy, art, literature — the human condition beyond science.

**Criteria:** Content addresses historical narratives, philosophical questions, artistic expression, cultural analysis.

**Examples:**《人类简史》《快乐的知识》《风景入画》《南京大屠杀》

**MindOS tags:** `domain: humanities` `topic: history|philosophy|art|literature`

**When to connect to Scholar Lens:** Rarely. These books build general human understanding, not clinical skills. The connection, if any, is to professional identity through broadened perspective — NOT to clinical reasoning.

---

### 4. Self-Understanding (自我理解)

Books about personal growth, relationships, emotions, identity — the inner world.

**Criteria:** Content addresses self-awareness, emotional life, interpersonal dynamics, personal values.

**Examples:**《和另一个自己谈谈心》《爱的艺术》《人间清醒恋爱指南》《走出抑郁》

**MindOS tags:** `domain: self` `topic: emotion|relationship|identity|growth`

**When to connect to Scholar Lens:** Indirectly. Understanding oneself is foundational to understanding patients. But this connection should be stated as a possibility, not a conclusion. "这可能帮助你理解患者的情绪体验（L1）" — never "你正在通过阅读提升医患沟通能力（L4）".

---

### 5. Interest & Leisure (兴趣娱乐)

Books read purely for enjoyment, curiosity, or aesthetic pleasure — no instrumental purpose.

**Criteria:** Reading motivated by enjoyment rather than growth goals. User's notes are sparse or purely appreciative.

**Examples:**《长安的荔枝》《你是我的全世界（漫画）》《我喜欢你笑起来》《手机摄影密码》

**MindOS tags:** `domain: leisure` `topic: fiction|comics|photography|poetry`

**When to connect to Scholar Lens:** Almost never. Leisure reading is valid in itself. It restores energy and provides balance. The only valid observation is: "本月娱乐阅读占比 X%，属于正常的恢复性阅读。"

---

### 6. Information Gathering (信息获取)

Books read to acquire specific facts, skills, or reference knowledge — pragmatic, not reflective.

**Criteria:** Reading is tool-like: learn a skill, solve a problem, answer a question.

**Examples:**《AI时代生存手册》《无伤跑法》《你是你吃出来的》

**MindOS tags:** `domain: information` `topic: technology|health|skill`

**When to connect to Scholar Lens:** Only if the skill directly relates to medical practice or study methods.

---

## Classification Rules for Claude

When analyzing reading data:

1. **Assign domain first** — before any interpretation. A book IS what it IS.
2. **Domain ≠ value judgment** — "leisure" is not worse than "professional". It's just different.
3. **One book can span two domains** — e.g., 《我们为什么要睡觉？》is both information (health) and cognition (sleep science). Name both.
4. **Domain assignment is a fact (L4)** — it's based on the book's actual content, not interpretation.
5. **Scholar lens is a hypothesis (L0-L2)** — it's an interpretation that requires evidence to strengthen.
6. **If multiple domains are present in a month's reading**, note the distribution. A balanced reading diet is normal and healthy.

## Domain → Scholar Lens Mapping (Conservative)

| Domain | Scholar Lens Connection | Default Confidence |
|--------|------------------------|-------------------|
| Professional | Direct — all five dimensions apply | L3-L4 |
| Cognition | Indirect — may connect to 临床思维, 学习效能 | L1 |
| Humanities | Minimal — may connect to 职业认同 (broadening perspective) | L0-L1 |
| Self | Indirect — may connect to 职业认同 (understanding people) | L1 |
| Leisure | None — valid in itself as recovery | N/A |
| Information | Context-dependent — only if skill is medical/study-related | L1-L2 |

**Key rule:** Never force a connection. "本月无明显专业关联信号" is a valid and important output.
