# 实施计划 — #3 payoff_clear(overstepping rubric 第三条腿)

- 日期:2026-07-03
- 分支:`feat/overstepping-eval-dimension`(当前;非 main)
- 前置:overstepping 维度已 commit(`bd341c9`);本增量在其上加一条 judge 腿
- 来源:讨论稿 §3 提案 #3 + 研究 P4 finding 4
- 状态:**plan-only,拿到 go 才写代码**

## Grill 决策(2026-07-03,已锁)

- **G1 作用域 = 窄版**:这个检查只在"工具删掉了一个假假设"时才运行;没删就不打分(不侵占未来 #2 clear-ask / #5 可读性)。
- **G2 打分 = 硬失败**:删完留下断裂/半截的句子 → 这道测试题判**不通过、要重做**(和"意思有没有保住"同级,是能翻转整题结果的硬指标,仅在适用时)。
- **G3 测试量 = 先一组英文对照**:一个"删后破句=不通过" + 一个"删得干净=通过";另给现有 4 道 overstepping 题也挂上这个检查(它们都是干净删除,应全通过)。中文对照等看到中英文表现不一致再补。

## Goal(可验证的 done)

给 overstepping rubric row 家族加一条 **`payoff_clear`** judge 腿:当一处**被制造的预设**按 **少写** 删掉后,核对**活下来的那句 Y 是否仍是完整、无歧义的陈述**——而不是丢了修辞脚手架、读起来像残句/非续的 stub。

**Done =** `pytest evals/` 全绿 + `run_all.sh` ALL PASSED + 校准仍在 30-40% band + 展示新 fixture 的 before/after 判分。

## Why(缺口)

现 rubric 只查 `overstepping_removed` + `meaning_preserved`,**从不查"删完之后那句还立不立得住"**。一个改写可以把「你以为 X,其实 Y」删成一个**孤立、读者接不上**的 Y——两条现有腿都会放行,但成品更差。payoff_clear 补这个盲点(Ogilvy 规则 9「让人清楚该 get 到什么」的味道)。

## 改动文件(5 个,全在当前分支)

1. **`evals/fixtures/rubric.md`**
   - Dimensions 表加一行 `payoff_clear`:PASS = 少写删除后,存活的 claim 是完整无歧义的独立陈述;FAIL = 读作 stub / 被截断 / 需要被删的脚手架才成立。
   - over-stepping 段 + judge-prompt block 各加一句:**payoff_clear 只在发生了 removal 时才有意义**(与 `overstepping_removed` 配对;没删就 N/A)。
2. **`evals/fixtures/fixtures.json`**
   - 给现有 4 个 overstepping fixtures 的 `rubric_focus` 加 `payoff_clear`(它们的 after 都是干净删除 → PASS 案例)。
   - **新增 1 组最小对照**:同一 before,两个 after——(a) 过度剥离成 stub(payoff_clear **FAIL**);(b) 删预设但留完整 Y(**PASS**)。给这条腿一个真正的判别信号(否则全 PASS = 无效标尺,违反你的 eval 校准律)。
   - 新 fixtures 均 **judge-only**(`expect_baseline=MISS`,detector 盲)→ **不进** detector 的 8-fixture 校准计数。
3. **`evals/fixtures/test_fixtures.py` / `test_calibration.py`**
   - 若测试枚举/校验维度白名单,把 `payoff_clear` 加进允许集;断言校准 band 不受影响(judge-only 被排除)。
4. **`_shared/patterns/overstepping-presumption.md`**
   - 少写段加一句:修复必须让 Y 独立清晰(交叉引用 payoff_clear),保持 pattern 文档与 rubric 同步。
5. **`CHANGELOG.md`** — `[Unreleased]` 加一条。

## 约束块(实施前你要确认的三件事)

**(1) 精确 pattern/术语**
- 维度名 = `payoff_clear`(snake_case,与现有维度一致)。
- "over-stepping" / "少写·多写" / "validity condition" 术语**逐字保留**,不改名。
- payoff_clear 与 `overstepping_removed` **配对**,允许 **N/A**(没发生 removal 时不判)。

**(2) 我不会做的事(fence)**
- 不碰 detector 代码;不加任何 0-100 分;不把 payoff_clear 并入 AI-tell 分数(Q2 契约)。
- 不动那 8 个 genre fixtures 的 band;不改现有维度名。
- 不 merge 到 main;不在本步做 #1/#2/#5/#7;不接 live judge(离线 SKIPPED)。
- 不新增依赖(stdlib-only 不变)。

**(3) repo/branch/文件范围**
- 分支 `feat/overstepping-eval-dimension`;仅上列 5 个文件。

## 完成后的下一步(你已定的 1→2)

#3 绿灯 + 你验收 → **PR/merge `feat/overstepping-eval-dimension`** → 新开 `feat/audit-report-template` 做 **#1**。
