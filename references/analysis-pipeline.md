# Analysis Pipeline — Three Layers

Input: structured data from weread-collection + diary entries (V0.2+).

## Layer 1: Surface (事实层)

Compute and display, no interpretation:

- **Total reading time** — current month, in hours+minutes. Trend vs previous month (↑/↓ %).
- **Active books** — count of books with readTime > 0 this month.
- **Reading days** — from `readDays`. Compare to calendar days in month.
- **Preferred categories** — from `preferCategory[]`. Top 3 with percentages.
- **Peak reading time** — from `preferTime[]`. Convert 6am-offset indices to actual hours.
- **Notes inventory** — total notes from all books (1698 historical for user 抹茶). Top 10 books by total notes with breakdown (highlights / thoughts / bookmarks).
- **Shelf stats** — total shelf items (books + albums + mp). 书单 names and their sizes.

## Layer 2: Association (关联层)

Connect dots — patterns emerge here:

### Category shifts
Compare current month's `preferCategory` distribution to previous month's:
- Which categories gained share?
- Which declined?
- Is this a one-month blip or a trajectory?

### Shelf booklists as mental maps
The user's `archive[]` names are self-created categories. Analyze:
- What domains has the user chosen to organize? (e.g., "技能训练" vs "时人不知心理学")
- Are there categories that suggest exploration of new territory?
- Are there categories that haven't been active recently?

### Scholar reclassification
Remap weread categories into dental growth dimensions:

| If book is in weread category... | ...consider it through this scholar lens |
|----------------------------------|----------------------------------------|
| 心理学 — 认知与行为, 心理学应用 | **临床决策思维** — cognitive bias → diagnostic reasoning |
| 心理学 — 社会心理学, 亲密关系 | **职业认同** — understanding people and relationships |
| 医学健康 — 医学 | **专业知识拓展** |
| 个人成长 — 认知思维, 人生哲学 | **学习效能** — metacognition about learning itself |
| 教育学习 — 教育 | **学习效能** — learning methodology |
| 文学, 艺术 | **恢复性阅读 + 人文素养** — energy recovery, not "escape" |
| 科学技术 — 科学科普 | **科研素养** — evidence evaluation |

Apply the reclassification to the top 10 books. Show: weread category → scholar dimension.

### Professional identity signals
Check for books that explore "what it means to be a doctor/medical professional":
- Memoirs by doctors (e.g., 《学医七年》)
- Hospital/clinical narratives (e.g., 《病房生死录》)
- Medical humanities

If present: flag as professional identity exploration signal.

## Layer 3: Narrative (叙事层)

Go beyond individual facts to the story they tell:

### Core narrative (1-2 sentences)
What is the user's reading REALLY about? Not "they read X and Y", but the underlying curiosity.

Example: "Your reading orbits a central question: how to make the mind and body function better — nutrition for the body, psychology for the self, learning methods for the mind."

### Direction of movement
Is the thinking moving somewhere? From what → toward what?

Example: "Reading focus shifting from efficiency optimization ('how to do more') toward understanding uncertainty ('how to face what I cannot control')."

### Reflection question
Generate ONE question that:
- Connects the reading pattern to the user's actual life
- Is open-ended (not yes/no)
- Invites self-examination without judgment
- ≤50 words

Example: "你在41本书里留下了1698条笔记——营养学、心理学、阅读方法。如果让你用一句话总结：这些书加在一起，你在找什么？"
