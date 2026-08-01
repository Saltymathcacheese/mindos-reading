---
action_id: ""
title: ""
source:
  pattern: null
  hypothesis: null
  created_from: null
created: {{date}}
status: "proposed"              # proposed | accepted | testing | completed | failed | abandoned
target_behavior: ""
success_metric:
  metric: ""
  baseline: 0
  target: 0
  scale: ""
friction:
  difficulty: 5                # 1-10, how hard is this to do?
  estimated_time_min: 0
  dependency: []               # What does this depend on? (sleep, motivation, environment...)
  failure_reason: null          # If abandoned/failed, WHY? (Not "didn't do it", but what blocked it)
outcome:
  result: null                  # success | partial | failure | unclear
  effect_size: null
  evidence: []
  user_reflection: null
last_reviewed: null
tags: []
---

# {{title}}

## 为什么要试这个
（AI 生成或用户填写——基于什么 pattern/hypothesis 提出的？）

## 执行记录
| 日期 | 执行了？ | 具体情况 | 结果指标 | 备注 |
|------|---------|---------|---------|------|
| | | | | |

## ⚡ 行动阻力
- 难度：__ /10
- 预计耗时：__ 分钟
- 依赖条件：
- 如果失败了，原因是什么：（不要写"没执行"，要写"什么阻碍了执行"）

## 结论
（这个 action 完成或放弃后填写）

### 结果
- 成功 / 部分有效 / 无效 / 不确定

### 学到了什么
（比结果更重要的是你从中学到了什么）

### 对相关 Pattern 的反馈
（这个结果支持还是削弱了触发它的 pattern？）
