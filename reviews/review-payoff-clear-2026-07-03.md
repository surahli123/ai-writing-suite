# 审查结论 + 修复计划 — #3 payoff_clear

- 日期:2026-07-03
- 审查方式:Workflow 编排 2 个 OMC subagent 并行(`oh-my-claudecode:code-reviewer` + `oh-my-claudecode:test-engineer`,Sonnet),独立上下文
- 运行:`wf_2297e8ea-717`;完整输出:`tasks/wan8dy7pw.output`
- 结论:**REQUEST CHANGES**(今天无红,但契约未落地 + 测试不守 diff)
- 状态:#3 已暂存**未提交**,修完再提交

## 两个 subagent 的收敛发现

### BLOCKER(test-engineer,实证)
`PayoffClearHardNegative` 不守 diff。git-stash 掉 fixtures.json/rubric.md/pattern 改动、只留 test_fixtures.py → 两个新测试仍 PASS,全套仍绿。它们喂罐装 dict 给**未改动的** `judge.aggregate`,只是把 `payoff_clear` 当任意标签复用了已有 `test_focus_dim_fail_forces_fail` 的逻辑。docstring "proves payoff_clear is a HARD focus leg" 为假(aggregate 无硬/软之分,所有 focus 维度本就 always-required)。

### CONCERN(code-reviewer,已复现)
`aggregate()` 无 "N/A/omit when no removal" 代码路径,而 rubric.md 三处 + judge-prompt 模板都承诺了它。`required = set(rubric_focus) | {no_fabrication}`;判官若按 N/A 省略 payoff_clear → 该 rep 视为不完整 → 丢弃 → 若无完整 rep → 返回 None → **整题静默 SKIP,吞掉真 FAIL**。潜伏(5 条实况题都保证有删除),但 ship 的契约未实现。

### 其余(都同意)
- CONCERN:N/A 语义文档 3× / 测试 0×;无 fixture 走 omit-when-no-removal 路径。
- CONCERN:over-stripped FAIL 搭档串只活在 docstring 注释里,从没跑过 `detector.analyze()`、没验证 detector_blind、没验证它和 clean-after 只差 payoff_clear。
- CONCERN(关键遗漏):**没有测试断言判官 prompt 模板含 PAYOFF-CLEAR CHECK** —— 这是 diff 里唯一"revert 后会变红"的守卫,却没写。
- SUGGESTION:PayoffClearHardNegative docstring "hard focus leg vs advisory" 读着自相矛盾;应澄清作用域(单题判定 vs CI 退出码)。
- SUGGESTION/NIT:live-judge 路径未验(全项目已知限制,非本 diff 引入);clean-after 测试也是罐装 fiat。

## 修复计划

### 必做(无论选哪条路)—— 用真守卫测试替掉戏
TDD 方式:每个新测试先确认**revert diff 后会变红**,再确认加回后变绿。
1. `test_judge_template_documents_payoff_clear` — 断言 `_extract_judge_template()` 含 `PAYOFF-CLEAR CHECK` + `payoff_clear`。**守 rubric.md 的判官块**(唯一真守卫)。
2. `test_payoff_clear_paired_with_overstepping_removed` — 任何 fixture 若 focus 含 payoff_clear,则必含 overstepping_removed。**守 fixtures.json + 锁配对不变量**。
3. `test_overstep05_failpartner_detector_blind_and_isolated` — 把 over-stripped FAIL 串**物化**成常量,跑 `analyze()` 断言 score==0 + 断言 presumption 短语('you might think')在 clean-after 与 stub 里都已消失(隔离 payoff_clear)。**守 claim-evidence**。
4. 重构 `PayoffClearHardNegative`:删掉"proves HARD focus leg"假声明,改名/改注释说明它测的是**通用 aggregate 语义**(或按 SUGGESTION 澄清作用域)。

### 决策点(要你拍)—— N/A 契约怎么办
- **A(最小,推荐)**:不碰共享的 `judge.py aggregate`。把 N/A 当**fixture 编写规则**(payoff_clear 只挂在保证有删除的题上,由守卫测试 #2 强制)+ 改 rubric 措辞,让给 live 判官的 N/A 提示不再暗示"省略→静默 SKIP"。#3 诚实收口,改动最小;live 判官遇到真 N/A 的边缘留作**记录在案的已知限制**。
- **B(治本)**:同时让 `aggregate()` 懂 N/A(解析显式第三态,从 required 里剔除),端到端强制契约。更正确,但**动到所有维度共享的核心判官逻辑**,要自带测试,scope 明显变大。

**我的推荐:A。** 理由:今天无红(潜伏),这是 v1 eval 增量,你的风格是"最小起步、只碰必要的";把 root-fix(B)留到有真实 N/A 需求或 live judge 上线时再做,并在 CHANGELOG 记为已知限制。
