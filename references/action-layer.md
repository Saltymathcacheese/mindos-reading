# Action Layer (V0.3+)

Do NOT load or apply unless version gate ≥ V0.3.

Actions are behavioral experiments. Not personality change mandates. Not "try harder."

## Action YAML Format

```yaml
action_id: "act_XXX"
title: "将晚间阅读提前30分钟"
source:
  pattern: "pat_001"
  hypothesis: "hyp_001-A"
  created_from: "[[2026-08-01-周报]]"
created: "2026-08-01"
status: "proposed"            # proposed|accepted|testing|completed|failed|abandoned
target_behavior: "晚间阅读结束时间从 23:00 提前到 22:30"
success_metric:
  metric: "次日学习效率自评"
  baseline: 4
  target: 6
  scale: "1-10 自评"
friction:
  difficulty: 5               # 1-10
  estimated_time_min: 0       # extra time cost
  dependency: ["需要在前一天晚上记得执行"]
  failure_reason: null        # filled only on failure/abandon
outcome:
  result: null                # success|partial|failure|unclear
  effect_size: null
  evidence: []
  user_reflection: null
last_reviewed: null
```

## Action Design Rules

Every action must:
1. Be small enough to execute within 7-14 days
2. Have a measurable outcome
3. NOT require personality change

❌ "提高自律"
❌ "减少焦虑"
✅ "连续7天22:30前结束非学习阅读"
✅ "每天写3句话日记，坚持14天"

## Action Lifecycle

```
proposed → accepted → testing → completed
    ↓           ↓         ↓
abandoned   abandoned    failed → archived
```

- **proposed:** AI suggested, user hasn't responded
- **accepted:** User agreed to try
- **testing:** Executing, collecting data
- **completed:** User confirmed effective
- **failed:** Tried but no effect
- **abandoned:** User rejected OR accepted but never executed

## Action Friction Analysis

When an action fails or is abandoned, do NOT conclude "user lacks discipline." Instead, analyze which friction dimension blocked execution:

1. **Goal problem?** — Was the target behavior unclear or misaligned with user's actual priorities?
2. **Environment problem?** — Did the physical/social environment prevent execution?
3. **Timing problem?** — Was the action scheduled at the wrong time of day/week?
4. **Energy problem?** — Did the user have the physical/mental energy needed?
5. **Design problem?** — Was the action itself poorly designed (too big, too vague, wrong success metric)?

Record the analysis in `action.friction.failure_reason`.

Example: "过去三个行动失败都发生在晚上10点以后——可能不是意志问题，而是执行时间设计问题。"

## Action ↔ Pattern Feedback

When an action completes:
- **Success** → pattern confidence +0.1, add evidence supporting linked hypothesis
- **Failure** → create or strengthen competing hypothesis candidate
- **User reflection** (even if action "failed") → may reveal a more important insight than the metric

The user's own words about the experience (`user_reflection`) are more valuable than the quantitative outcome.
