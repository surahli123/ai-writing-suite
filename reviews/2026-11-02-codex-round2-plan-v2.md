# Codex round-2 review: plan v2 (2026-11-02)

VERIFIED_AGAINST: claude/laughing-rubin-mkkadx-s9-lists-review @ 621d9e4 (fetched via GitHub API; local clone at c6f6367)
MODEL: Codex 6.1 Astra, reasoning=medium, run by the owner locally (read-only). Report pasted by the owner and reproduced verbatim. Its evidence directory (`reviews/step9-v2-review/`: plan snapshot, probe.py, probe-results.json) lives in the owner's local clone only and is not in this repository.
Disposition: docs/plan-step9-and-comms-shape-2026-11-02.md, "Review log (round 2)".

---

Step 9 / comms-shape 方案 v2 复审

**结论：Conditional No（不建议按当前文字直接实施）**；保留整体设计，修正下列 7 项后再进入实施。Step 9 不需要重做 A–G 的范围；Step 10 的状态机与 pilot 定位可以保留，主要修正评测依据。没有 P0，保留 2 项 P1、5 项 P2。

## 核验范围

- 核验时间：2026-11-01 America/Los_Angeles（2026-11-02 UTC）。
- 仓库：`surahli123/ai-writing-suite`。
- 固定远端提交：`621d9e4a0b55c1f9e91c909aaaf7c20fe1db8cbb`，分支 `claude/laughing-rubin-mkkadx-s9-lists-review`。
- 远端方案（固定提交）；审查输入快照 (reviews/step9-v2-review/plan-v2-source.md)。下文 P 行号均指该快照。
- 当前工作区仍为旧提交 `c6f6367`。本次通过 GitHub API 获取固定提交的完整快照，未切换分支、更新 `.git`、修改 canonical 方案或实现文件。
- 对照了 v1 的 Codex/Fable 审查记录、v2 review log、现有 checker 与原评测协议。未重新执行整套单元测试或收费行为评测；本轮不是实现验收。

## 保留的问题与最小修改

### R1 · P1 · 状态 oracle 按位置匹配，会放过实体状态交换

**位置：**P:131–135；targeted eval 中的状态检查项。

方案规定等长列表按位置匹配。反例：

```
before: Investigating LOGIN-1 / Fixed CHECKOUT-2
after:  Investigating CHECKOUT-2 / Fixed LOGIN-1
```

位置上的状态始终是 `[in progress, done]`，所以没有 upward move；但 LOGIN-1 已被错误地标成完成。反之，仅交换完整条目的顺序，会被位置算法误报。该 oracle 又参与阻断判定，因此不是普通实现细节。

**建议替换 P:133：**无论数量是否相等，先按唯一 ticket ID 或无歧义实体对齐；仅在确认实体一致时使用位置。无法对齐应记为 unscored，并报告覆盖缺口，不能算通过。保留交换状态 mutant，新增忠实重排 control。

**验证：**审查脚本模拟的是方案算法，不是尚未实现的 status checker。交换实体得到 `positional_flags=[]`、`entity_flags=['LOGIN-1']`；忠实重排得到相反结果。

### R2 · P1 · 把有限 fabrication 检查当成完整 traceability，会给错误放行依据

**位置：**P:450–461；`skills/ai-writing-suite/evals/fixtures/run_draft_cases.py:293–315`。

`find_fabrications` 明确仅覆盖数字、部分专名及封闭动词集合；它不枚举全部 claim，也不判断所有 claim 是否受来源支持。实际调用：

```
source: We fixed the login bug. We are investigating checkout failures.
output: The product is secure and reliable. Customer satisfaction improved.
find_fabrications -> []
```

正对照 `Churn fell 23%.` 则返回 `['23%']`，确认不是调用失败。问题是方案新赋予它“来源可追溯性”与 trial gate 的职责，超出了这个已有工具的能力；无需把工具改成通用事实核查器。

**建议：**将其改称 bounded fabrication screen，作为辅助信号。由看得到 packet 和实际揭示答案、看不到 arm 的 judge 建立 claim→source 清单，记录 supported / unsupported / declared gap；用该清单计算 traceability 与 unsupported-claim 数量，并驱动试用门槛。加入普通无来源断言的正对照。作者对模型建议的认可不能自动充当事实证据，继续遵守方案 “When the author insists” 的 `[NEEDS: evidence]` 规则。

### R3 · P2 · review-only 样本没有适用的失败门槛

**位置：**P:292–302。

Harm rule 要求“s9 失败且 s8 不失败”才阻断；紧接着又规定 review 样本只评 s9。于是新引用格式、诚实 strengths 等 oracle 失败时，没有定义应如何进入阻断结论。旧样本的 regression gate 不能替代这些新能力检查。

**建议：**拆开两条规则：共享 rewrite oracle 保留相对 s8 的 harm rule；review-only 的预注册 oracle 对 s9 做绝对通过检查，失败阻断对应 D/E 提交。不要为了获得比较值，让 s8 执行它从未承诺的新格式。语义项的评分方法在运行前固定。

### R4 · P2 · 每个字符串出现足够次数，不等于不同来源 occurrence

**位置：**P:178–204。

对 `Moreover, the dashboard is fast.`，分别引用 `Moreover` 与 `Moreover,`，两个字符串都在原文出现一次，满足 P:204 的逐字符串次数条件，却重复使用同一个连接词位置。该条件仍不能实现 v1 审查要求的独立 occurrence。

**建议：**同一个 finding 内，将引用分配到不同、互不重叠的来源跨度；不同 tell 之间允许引用同一句。保留重复原文的合法多次引用 control，增加同一位置不同长度片段的 mutant。这只验证来源位置，是否真的构成该 tell 仍交给语义判定。

### R5 · P2 · Fix 数字的字面成员检查会误拒合法改写

**位置：**P:171–174、206；`run_draft_cases.py:321`。

`3 views` 改成 `three views` 没有新增数量，但 `three` 不在原稿中，会被所写规则拒绝。`[NEEDS: …]` 又是方案允许的缺证输出；占位符中的数字不是已经断言的事实。现有 fabrication helper 已有剔除 NEEDS span 的先例。

**建议：**仅检查 Fix 中实际断言的替换文本，排除明确的 NEEDS span；对受支持的数字形式使用规范化数值及单位比较，而非字面 token membership。无法解析的形式报告覆盖边界；继续用 judge 检查语义造假。增加数字/英文数词等价及缺证占位符 control。

### R6 · P2 · cost 门槛的比较方向应写清

**位置：**P:450–462。

成本指标是 author turns、输入输出字符或 token；但 P:461 对 traceability 和 cost 一起使用 `≥ bare-staged`。按字面执行，会奖励更贵的流程。即使原意是“表现不差”，也不应由分析脚本作者猜测方向。

**建议替换：**`traceability at least as high as bare-staged OR cost no higher than bare-staged`，并在运行前固定哪一个已列成本指标用于这一条件，其他成本分开报告。保留 unsupported-claims 条件、无改善时的明确披露以及 owner 的最终 ship 决定。

### R7 · P2 · light-edit 禁止词序调整与保留语法修复权限冲突

**位置：**P:123；现有 `comms-polish/SKILL.md:107–118`。

`no word reordering inside items` 是绝对措辞，但同句又保留 grammar / ambiguity 修复。例如 `We the login bug fixed` → `We fixed the login bug` 是语法修复，也必须调整词序。上层“no list-structure transformations”可以表达正确意图，具体禁令却比它更宽。

**建议：**改为“不为统一列表 frame 或把 distinguishing word 放到首位而重排词序；修复语法或歧义所必需的局部词序调整仍允许”。继续禁止 light-edit 下的 frame unification 和 prefix moves。

## 已解决，不重新打开

- Praise 的字符串 overlap 硬拒已删除；同句不同属性可以分别赞扬和批评。遵守 owner 裁决。
- Parallel set 采用语义和共同容器，排除独立分发文本；统一 frame 已由义务改为有理由的许可。
- mixed-mode 整篇交付、short/long/skip 路径、re-confirm 条件、provenance ledger 已补齐。
- 新的 consistency report-only section 与 Notes 类别已明确。
- capability 依赖、旧 `comms-draft` scope 的读取兼容与历史资料保留已覆盖。
- detector/catalog 分歧明确延后，不用 detector 绿灯证明新规则有效。
- Step 10 改为 pilot、增加 bare-staged、共用预算，不再据 8 个 packet 声称非劣。
- 首轮 intake 仍最多 3 问；不是取消上限。本轮早期进展中的相反表述已纠正。

## 验证与覆盖

- 五个独立子审查均完成：coherence、feasibility、adversarial、scope-guardian、design-lens。范围与交互流程审查没有新增保留问题。
- 原始 9 项发现去重为以上 7 项；R1/R2 各由 feasibility 与 adversarial 独立提出，并由主审运行反例复核。原始结果位于证据目录 (reviews/step9-v2-review)。
- 可复现脚本 (reviews/step9-v2-review/probe.py) 与输出 (reviews/step9-v2-review/probe-results.json)。命令：

```
PYTHONDONTWRITEBYTECODE=1 python3 reviews/step9-v2-review/probe.py /path/to/621d9e4-snapshot
```

- 脚本验证：按位置与实体比较的差别、实际 fabrication helper 的漏检及正对照、重叠片段的字符串计数、数词成员检查反例。它不代表尚未实现功能已经经过测试。
- Cross-model adversarial 与 whole-document 两个任务都在传输前因 npm `EPERM` 退出，没有发送方案内容，也没有可采纳的跨模型输出。日志保留在证据目录；已收集并清理这两个任务目录。没有完成新的 Fable 复审，不把本轮称为 Codex + Fable 双方批准。
- 本次仅新增本地审查产物；没有修改 canonical 方案、实现代码，没有 commit、push 或 PR。所有建议尚未应用。

**完成条件：**以上 7 项落实到方案后，可对修改点做定向复核；不需要重新争论已采纳的产品方向。实现授权、owner 约 10 项盲标及真实文档试用仍按方案自己的阶段处理，本次审查不代替这些结果。
