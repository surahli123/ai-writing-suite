# 实施计划 — #1 审计报告输出模板(comms-polish detect/review)

- 日期:2026-07-03
- 分支:`feat/audit-report-template`(已建;非 main)
- 来源:讨论稿 §3 提案 #1(5 reader 里 2 个独立收敛的最高优先项)
- 状态:**plan-only,拿到 go 才写代码**

## Goal(可验证的 done)

把 comms-polish 的 `detect`/`review` 模式那句含糊输出(`SKILL.md:245`「lead with findings and examples, grouped by severity」)换成一个**固定审计报告模板**:

1. **一句话总评**——点名 draft 里最大的单个问题(worst-offender),不发 0-100 数字。
2. **findings 按命名分级**:**Critical**(改变含义/可信度)/ **Moderate**(可读性/AI 味)/ **Minor**(风格小疵),每条 = 原句引用 → tell 名 → 为什么 → 具体改法。
3. **收尾 "What's working" 清单**(2–3 处,给理由不是夸)——把内部 Safety Rules(`147-153`)的 preserve 意图显性化成用户可见交付物,防止后续编辑改坏好段落。

**Done =**(a)skill 仍能加载(`evals/test_skill_manifests.py` 绿,frontmatter/manifest 不破);(b)**demo**:拿一段 AI 味草稿跑 detect/review,展示输出确实按模板(总评句 + 分级 quote→why→fix + What's working)。

## Why

2 个 reader 独立收敛(P1 全部 + P5 finding 3):现行第 245 行含糊到 agent 可用**转述**代替**原句**、severity 无命名分级、无一句话总评、preserve 清单从不外显。一处模板改动关掉 4 个 gap。

## 改动文件(2–3 个)

1. **`skills/comms-polish/SKILL.md`** — 重写 `## Output`(242-247)里 detect/review 那一条为上述模板契约;在附近定义三层 severity(明确与 204-210 的 0-100 整体分**区分**);加 "What's working" 要求;附一个简短 worked example。
2. **`CHANGELOG.md`** — `[Unreleased]` 加一条。
3. **(可选)`evals/test_skill_manifests.py`(或新增小测)** — 断言 comms-polish Output 段包含三层命名分级 + "What's working"(廉价回归守卫,类似现有 manifest 测试;revert 即红)。

## 约束块(实施前确认三点)

**(1) 术语**
- 每条 finding 分级 = **Critical / Moderate / Minor**;整体 0-100 分数带(Pristine/Mostly human/…)**保持不动、语义分开**,绝不混为一谈。
- "What's working" 限 2–3 条、附理由。

**(2) 我不会做的(fence)**
- 只改 **detect/review** 输出;**rewrite mode**(244,返回纯润色文)与 **edit mode**(246)**不动**——mode 防火墙(讨论稿 tension #4)。
- **不碰** detector / eval fixtures / rubric / 判官维度;#1 纯输出格式,不是新维度,不进 30-40% 校准那套。
- 不动 main;不加依赖;不 wholesale 重写 SKILL.md 其它段。

**(3) 范围**
- 分支 `feat/audit-report-template`;仅上列 2–3 文件。

## 完成后

demo 通过 + 你验收 → commit(feature 1 个 + 可选 docs)→ PR。是否 merge / 是否接着做 #2(CTA)或先 wrapup,届时再定。
