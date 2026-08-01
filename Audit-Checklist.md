# MindOS v3.4 Architecture Compliance Audit Checklist

> 给 Claude Code / Claude Agent 自动审计用。
> 用法：将本文件 + CLAUDE_DEVELOPMENT_GUIDE.md 一并交给 Claude，指令：
> "根据 CLAUDE_DEVELOPMENT_GUIDE.md 和 Audit-Checklist.md，对当前 MindOS 仓库进行 v3.4 架构符合性检查。输出差距报告，不修改代码。每条逐项标记 ✅/⚠️/❌。"

---

## A. 目录结构完整性

| # | 检查项 | 预期 | 当前状态 |
|---|--------|------|----------|
| A1 | 根目录存在 `SKILL.md` | 必须 | ✅ |
| A2 | 存在 `references/` 目录，含 ≥10 个 .md 文件 | 必须 | ✅ 12 files |
| A3 | 存在 `schemas/` 目录，含 ≥3 个 .schema.json | 必须 | ✅ 5 files |
| A4 | 存在 `scripts/mindos.py`（统一入口） | 必须 | ✅ |
| A5 | 存在 `scripts/preflight.py`（状态加载器） | 必须 | ✅ |
| A6 | 存在 `scripts/weread_fetch.py`（数据采集） | 必须 | ✅ |
| A7 | 存在 `scripts/state_update.py`（状态更新） | 必须 | ✅ |
| A8 | 存在 `scripts/vault_check.py`（环境检查） | 必须 | ✅ |
| A9 | 存在 `scripts/validate_state.py` | 必须 | ✅ |
| A10 | 存在 `scripts/validate_response.py` | 必须 | ✅ |
| A11 | 存在 `scripts/validate_report.py` | 必须 | ✅ |
| A12 | 存在 `tests/` 目录，含 ≥10 个 test_*.py | 必须 | ✅ 17 files |
| A13 | 存在 `handoff/` 目录（Python↔Claude 协议） | 必须 | ✅ |
| A14 | 存在 `evaluation/` 目录 | 必须 | ✅ |
| A15 | 存在 `config.yaml.example` | 必须 | ✅ |
| A16 | 存在 `.env.example` | 必须 | ✅ |
| A17 | 存在 `requirements.txt` | 必须 | ✅ |
| A18 | 存在 `Templates/` 目录 | 必须 | ✅ |
| A19 | 存在数编号 Obsidian 目录（0-Inbox, 1-Experiences, 2-Knowledge, 3-Patterns, 4-Questions, 5-Decisions, 6-Reviews, 7-System, 8-Goals, 9-Actions, 10-Memory, 11-Capture, 12-Knowledge-Map） | 建议 | ⚠️ 待逐项确认 |

---

## B. SKILL.md 纯度检查

| # | 检查项 | 验证方法 |
|---|--------|----------|
| B1 | SKILL.md ≤ 150 行 | `wc -l SKILL.md` |
| B2 | 不含大段推理规则（应放 references/） | 全文搜索"你应该""心理学""人格""诊断" |
| B3 | 含 Trigger Routing 表格 | grep "Trigger Routing\|触发词\|User says" |
| B4 | 含 Cognitive Handoff 协议说明 | grep "handoff\|analysis_request\|analysis_response" |
| B5 | 含错误处理表格 | grep "Error\|错误" |
| B6 | 含版本门控逻辑（V0.1/V0.2/V0.3） | grep "V0.1\|V0.2\|V0.3\|版本\|version gate" |
| B7 | 含安全声明 | grep "安全\|safety\|no diagnosis\|不诊断" |

---

## C. Python 代码规范检查（scripts/ 下所有 .py）

| # | 检查项 | 验证方法 |
|---|--------|----------|
| C1 | 所有 .py 文件包含 `from __future__ import annotations` | 全局 grep（Python 3.11+） |
| C2 | 所有 public 函数有 type hints | 人工抽查 5 个核心脚本 |
| C3 | 无裸 `print()`（应用 `logging.info()`） | `grep -rn "print(" scripts/ | grep -v "logging"` |
| C4 | 所有 CLI 脚本输出 JSON 到 stdout | 抽查 mindos.py / preflight.py / weread_fetch.py |
| C5 | 错误返回统一格式 `{"success": false, "error": "..."}` | grep 各脚本 error 处理 |
| C6 | YAML 操作使用 `ruamel.yaml`（非 PyYAML） | `grep -rn "import yaml\|from yaml\|ruamel" scripts/` |
| C7 | 无硬编码 API key | `grep -rn "wrk-\|sk-\|api_key.*=\|key.*=.*['\"][A-Za-z0-9_-]{20,}" scripts/` 不匹配 |
| C8 | 无硬编码绝对路径 | `grep -rn "/home/\|C:\\\\\|Users\\\\" scripts/` 不匹配 |
| C9 | 无心理推断逻辑（"personality""extrovert""introvert""anxiety" 等词不应出现在 Python 中） | `grep -rni "personality\|extrovert\|introvert\|anxiety\|depressi\|perfectionist" scripts/` 无匹配 |

---

## D. Reference 层纯度检查

| # | 检查项 | 验证方法 |
|---|--------|----------|
| D1 | references/ 下所有文件为 .md 格式（非 .py） | `find references/ -type f ! -name "*.md"` 无输出 |
| D2 | 每个 reference 文件有明确主题 | 读取前 5 行检查是否有 H1 标题 |
| D3 | references/ 不含可执行代码（Python/Shell） | `grep -rn "\`\`\`python\|\`\`\`bash\|subprocess\|import " references/` — 仅允许示例代码块，不允许实际运行逻辑 |
| D4 | 存在 `confidence-system.md` | ✅ 确认存在 |
| D5 | 存在 `analysis-pipeline.md` | ✅ 确认存在 |
| D6 | 存在 `output-templates.md` | ✅ 确认存在 |
| D7 | 存在 `pattern-engine.md` | ✅ 确认存在 |
| D8 | 存在 `hypothesis-framework.md` | ✅ 确认存在 |

---

## E. Schema 层完整性

| # | 检查项 | 验证方法 |
|---|--------|----------|
| E1 | `weread_output.schema.json` — 微信读书 API 输出结构 | `cat schemas/weread_output.schema.json \| python -m json.tool` 合法 |
| E2 | `analysis_state.schema.json` — 运行时状态结构 | 同上 |
| E3 | `claude_response.schema.json` — Claude 认知响应结构 | 同上 |
| E4 | `report.schema.json` — 报告输出结构 | 同上 |
| E5 | `memory.schema.json` — 记忆压缩结构 | 同上 |
| E6 | Schema 中无 Python 逻辑（仅 JSON Schema 声明） | 检查各 schema 文件不含 `import` / `exec` / 内联 Python |

---

## F. Handoff 协议完整性

| # | 检查项 | 验证方法 |
|---|--------|----------|
| F1 | `handoff/analysis_request.json.example` 存在 | ✅ 确认存在 |
| F2 | `handoff/analysis_response.json.example` 存在 | ✅ 确认存在 |
| F3 | request 结构对应 `claude_response.schema.json` | 比对 example 与 schema |
| F4 | response 结构对应 `claude_response.schema.json` | 同上 |
| F5 | handoff 文件不含 Python 执行逻辑 | 检查文件内容 |

---

## G. 测试覆盖

| # | 检查项 | 验证方法 |
|---|--------|----------|
| G1 | `pytest tests/ -v` 通过率 ≥ 90% | 运行测试 |
| G2 | 存在 `test_preflight.py` | ✅ |
| G3 | 存在 `test_weread_parser.py` | ✅ |
| G4 | 存在 `test_state_update.py` | ✅ |
| G5 | 存在 `test_vault_check.py` | ✅ |
| G6 | 存在 `test_mindos_runtime.py` | ✅ |
| G7 | 存在 `test_handoff.py` | ✅ |
| G8 | 存在 `test_report_pipeline.py` | ✅ |
| G9 | 存在 `test_report_schema.py` | ✅ |
| G10 | 存在 `test_memory.py` | ✅ |
| G11 | 存在 `test_evaluation.py` | ✅ |
| G12 | 存在 `test_regression.py` | ✅ |
| G13 | 存在 `test_validate_report.py` | ✅ |
| G14 | 存在 `test_validate_state.py` | ✅ |

---

## H. 认知安全合规

| # | 检查项 | 验证方法 |
|---|--------|----------|
| H1 | SKILL.md 含 "你不是心理学家" 等效声明 | grep "不是心理\|not a psycholog\|不诊断\|no diagnosis" |
| H2 | SKILL.md 含 confidence 等级说明（L0-L4） | grep "L0\|L1\|L2\|L3\|L4\|confidence" |
| H3 | SKILL.md 含隐私声明（日记引用 ≤50 字符） | grep "50\|隐私\|privacy\|diary.*quote" |
| H4 | references/ 下含安全规则或互动规则文件 | ✅ `interaction-rules.md` 存在 |
| H5 | 报告模板不含人格标签（"你是 X 类型的人"） | 检查 `references/output-templates.md` |
| H6 | schema 不含 `diagnosis` / `personality_type` 字段 | grep 各 schema |

---

## I. 运行时健康检查

| # | 检查项 | 验证方法 |
|---|--------|----------|
| I1 | `python scripts/mindos.py check` 返回 `healthy: true` | 执行 |
| I2 | `python scripts/mindos.py status` 返回有效 JSON | 执行 |
| I3 | `python scripts/mindos.py validate` 不崩溃 | 执行 |
| I4 | `python scripts/preflight.py .` 返回 mode + diary_count | 执行 |
| I5 | `python scripts/vault_check.py .` 独立可运行 | 执行 |
| I6 | `python scripts/validate_state.py .` 独立可运行 | 执行 |

---

## J. 架构边界合规（v3.4 冻结规则）

| # | 检查项 | 违规示例 | 验证方法 |
|---|--------|----------|----------|
| J1 | Python 不做认知推理 | `if user_is_stressed: suggest_meditation()` | 审查 scripts/ 下每个 .py 前 30 行 + 搜索 "suggest""recommend""should""你应该" |
| J2 | references 不含可执行代码 | `references/` 中出现 `subprocess.run()` | grep 可执行模式 |
| J3 | SKILL.md 仅路由，不长篇推理 | SKILL.md > 200 行 | wc -l |
| J4 | 每个新数据结构有对应 schema | 新增 YAML/JSON 结构无 schema 覆盖 | 比对 7-System/ 下 .yaml 数与 schemas/ 下 .schema.json 数 |
| J5 | 不合并独立模块 | 多个 .py 功能挤进一个文件 | 检查 mindos.py 行数是否合理（当前 209 行 ✅） |
| J6 | 不删除现有功能 | 某次 commit 删除了整个模块 | git diff 扫描 |

---

## K. v3.4 → v4 迁移就绪检查（仅评估，不修改）

| # | 检查项 | 当前状态 |
|---|--------|----------|
| K1 | 9-Actions/ 目录存在且有索引 | ✅ ACTIONS-INDEX.md 存在 |
| K2 | 8-Goals/ 目录存在且有索引 | ✅ GOALS-INDEX.md 存在 |
| K3 | 10-Memory/ 目录存在且有索引 | ✅ MEMORY-INDEX.md 存在 |
| K4 | Action-Template.md 存在 | ✅ |
| K5 | memory-compression.md 存在于 references/ | ✅ |
| K6 | action-layer.md 存在于 references/ | ✅ |
| K7 | interaction_state.yaml 存在于 7-System/ | ✅ |
| K8 | memory_collector.py / memory_scorer.py / memory_validator.py 存在于 scripts/ | ✅ 三件齐全 |
| K9 | calibration_engine.py / prediction_tracker.py / feedback_processor.py 存在于 scripts/ | ✅ |
| K10 | memory.schema.json 存在于 schemas/ | ✅ |

---

## 审计输出格式

执行审计时输出：

```markdown
# MindOS v3.4 架构符合性审计报告
日期: YYYY-MM-DD
审计范围: MindVault/书适圈/

## 汇总
- ✅ 通过: X 项
- ⚠️ 警告: Y 项
- ❌ 失败: Z 项

## 失败项详情
| 编号 | 检查项 | 发现 | 建议修复 |
|------|--------|------|----------|
| C3 | 无裸 print() | scripts/xxx.py:42 发现 print("debug") | 替换为 logging.debug() |

## 警告项
| 编号 | 检查项 | 发现 | 说明 |
|------|--------|------|------|

## 结论
[架构健康度评估：优秀/良好/需修复/严重偏离]
```

---

**本清单版本:** 1.0
**对应 MindOS 版本:** v3.4
**最后更新:** 2026-08-01
