# Hypothesis Framework (V0.3+)

Do NOT load or apply unless version gate ≥ V0.3.

## Hypothesis Tiers

Not everything deserves competing hypothesis analysis:

| Tier | Scope | Max Active | Requires Competing? |
|------|-------|-----------|---------------------|
| 1 | 普通观察 — "本周阅读量增加" | Unlimited | No |
| 2 | 行为模式 — "可能与压力相关" | 5 | No |
| 3 | 重大人生模式 — career, identity, values | 2 | **Yes — must have null hypothesis** |

Tier 3 ONLY enables the full competing-hypothesis machinery.

## Competing Hypothesis Structure (Tier 3)

For a given observation, maintain 3+ candidate explanations:

```yaml
candidates:
  - id: "hyp_X-A"
    statement: "晚间阅读导致睡眠减少，直接影响次日精力"
    type: "direct_causal"
    prior_probability: 0.60
    evidence_for: [...]
    evidence_against: [...]
    test: "如果 action_001 成功改善效率 → 支持 A"

  - id: "hyp_X-B"
    statement: "考试压力增大，同时导致学习效率下降和阅读增加"
    type: "common_cause"
    prior_probability: 0.30
    evidence_for: [...]
    evidence_against: [...]
    test: "如果考试周结束后模式消失 → 支持 B"

  - id: "hyp_X-C"
    statement: "次日效率波动只是随机现象"
    type: "random"               # <-- null hypothesis, ALWAYS present
    prior_probability: 0.10
    evidence_for: [...]
    evidence_against: [...]
```

## Decision Rules

1. Only raise a candidate's confidence when its evidence_for significantly outweighs evidence_against.
2. Two candidates with equal evidence → maintain ambiguity, mark "需更多数据".
3. Candidate C (random/null) is always retained — only dismissed when data clearly contradicts.

## Output Format

❌ "晚间阅读降低次日效率"
✅ "观察：晚间阅读↑、次日效率↓。三种解释：A) 阅读→睡眠↓→效率↓；B) 考试压力同时驱动两者；C) 随机波动。目前 A 证据最多但未排除 B。建议执行 [[act_001]] 测试 A，同时观察考试周后模式是否消失以测试 B。"
